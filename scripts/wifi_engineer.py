#!/usr/bin/env python3
"""WIFI_ESPECIALISTA Network Engineer Toolkit: safe, cross-platform diagnostics."""
from __future__ import annotations
import argparse, csv, ipaddress, json, platform, shutil, socket, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"

class DiagnosticError(RuntimeError):
    pass

def run_command(args: list[str], timeout: float = 10.0) -> dict[str, Any]:
    """Run a fixed argument vector without a shell and enforce a timeout."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False, shell=False)
        return {"command": args, "returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except FileNotFoundError:
        return {"command": args, "returncode": 127, "stdout": "", "stderr": "Command not found"}
    except subprocess.TimeoutExpired:
        return {"command": args, "returncode": 124, "stdout": "", "stderr": "Command timed out"}

def os_family() -> str:
    s = platform.system().lower()
    return {"windows":"windows", "linux":"linux", "darwin":"macos"}.get(s, s)

def system_info() -> dict[str, Any]:
    return {"hostname":socket.gethostname(), "platform":platform.platform(), "system":platform.system(),
            "release":platform.release(), "python":platform.python_version(),
            "timestamp_utc":datetime.now(timezone.utc).isoformat()}

def interface_inventory() -> dict[str, Any]:
    osn=os_family()
    cmd={"windows":["ipconfig","/all"], "linux":["ip","-details","-statistics","address","show"],
         "macos":["ifconfig","-a"]}.get(osn)
    if not cmd: raise DiagnosticError(f"Unsupported operating system: {osn}")
    r=run_command(cmd); r["platform"]=osn; return r

def route_inventory() -> dict[str, Any]:
    osn=os_family()
    cmd={"windows":["route","print"], "linux":["ip","route","show","table","all"],
         "macos":["netstat","-rn"]}.get(osn)
    if not cmd: raise DiagnosticError(f"Unsupported operating system: {osn}")
    r=run_command(cmd); r["platform"]=osn; return r

def wifi_inventory() -> dict[str, Any]:
    osn=os_family()
    if osn=="windows": commands=[["netsh","wlan","show","interfaces"],["netsh","wlan","show","networks","mode=bssid"]]
    elif osn=="linux":
        if shutil.which("nmcli"):
            commands=[["nmcli","-f","IN-USE,SSID,BSSID,CHAN,FREQ,RATE,SIGNAL,SECURITY","device","wifi","list"]]
        elif shutil.which("iw"): commands=[["iw","dev"]]
        else: return {"returncode":127,"stderr":"Install NetworkManager (nmcli) or iw"}
    elif osn=="macos":
        airport="/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
        if not Path(airport).exists(): return {"returncode":127,"stderr":"Native airport utility unavailable"}
        commands=[[airport,"-I"]]
    else: raise DiagnosticError(f"Unsupported operating system: {osn}")
    return {"platform":osn,"results":[run_command(c) for c in commands]}

def calculate_network(value: str) -> dict[str, Any]:
    try: interface=ipaddress.ip_interface(value)
    except ValueError as e: raise DiagnosticError(f"Invalid address/CIDR: {e}") from e
    n=interface.network
    result={"input":value,"version":interface.version,"ip":str(interface.ip),"prefix_length":n.prefixlen,
            "netmask":str(n.netmask),"network":str(n.network_address),
            "broadcast":str(n.broadcast_address) if interface.version==4 else None,
            "first_usable":None,"last_usable":None,"num_addresses":n.num_addresses,
            "is_private":interface.ip.is_private,"is_global":interface.ip.is_global}
    if interface.version==4 and n.num_addresses>2:
        result["first_usable"]=str(n.network_address+1); result["last_usable"]=str(n.broadcast_address-1)
    elif interface.version==4 and n.num_addresses==2:
        result["first_usable"]=str(n.network_address); result["last_usable"]=str(n.broadcast_address)
    elif interface.version==6 and n.num_addresses>1:
        result["first_usable"]=str(n.network_address+1); result["last_usable"]=str(n.broadcast_address)
    return result

def resolve_dns(hostname: str, record_type: str="ALL") -> dict[str, Any]:
    if record_type not in {"A","AAAA","ALL"}: raise DiagnosticError("Supported types: A, AAAA, ALL")
    family={"A":socket.AF_INET,"AAAA":socket.AF_INET6,"ALL":socket.AF_UNSPEC}[record_type]
    try: rows=socket.getaddrinfo(hostname,None,family,socket.SOCK_STREAM)
    except socket.gaierror as e: return {"hostname":hostname,"record_type":record_type,"error":str(e),"addresses":[]}
    return {"hostname":hostname,"record_type":record_type,"addresses":sorted({x[4][0] for x in rows})}

def ping_host(host: str,count: int=4,timeout: float=3.0) -> dict[str, Any]:
    if not 1<=count<=20: raise DiagnosticError("Ping count must be between 1 and 20")
    if not 0<timeout<=30: raise DiagnosticError("Timeout must be > 0 and <= 30 seconds")
    osn=os_family()
    if osn=="windows": cmd=["ping","-n",str(count),"-w",str(int(timeout*1000)),host]
    elif osn in {"linux","macos"}: cmd=["ping","-c",str(count),"-W",str(max(1,int(timeout))),host]
    else: raise DiagnosticError(f"Unsupported operating system: {osn}")
    r=run_command(cmd,count*timeout+5); r["target"]=host; return r

def trace_route(host: str,max_hops: int=20) -> dict[str, Any]:
    if not 1<=max_hops<=64: raise DiagnosticError("Max hops must be between 1 and 64")
    osn=os_family()
    if osn=="windows": cmd=["tracert","-d","-h",str(max_hops),"-w","1000",host]
    elif osn in {"linux","macos"}:
        exe=shutil.which("traceroute")
        if not exe: return {"target":host,"returncode":127,"stderr":"Install traceroute"}
        cmd=[exe,"-n","-m",str(max_hops),"-w","1",host]
    else: raise DiagnosticError(f"Unsupported operating system: {osn}")
    r=run_command(cmd,max_hops*2+10); r["target"]=host; return r

def tcp_check(host: str,port: int,timeout: float=3.0) -> dict[str, Any]:
    if not 1<=port<=65535: raise DiagnosticError("TCP port must be between 1 and 65535")
    if not 0<timeout<=15: raise DiagnosticError("Timeout must be > 0 and <= 15 seconds")
    start=time.perf_counter()
    try:
        with socket.create_connection((host,port),timeout=timeout): ok=True; error=None
    except OSError as e: ok=False; error=str(e)
    result={"host":host,"port":port,"reachable":ok,"latency_ms":round((time.perf_counter()-start)*1000,2)}
    if error: result["error"]=error
    return result

def passive_neighbors() -> dict[str, Any]:
    osn=os_family()
    cmd={"windows":["arp","-a"],"linux":["ip","neighbor","show"],"macos":["arp","-an"]}.get(osn)
    if not cmd: raise DiagnosticError(f"Unsupported operating system: {osn}")
    r=run_command(cmd); r["note"]="Passive local cache only; no subnet scan performed."; return r

def collect_report(include_wifi: bool=True) -> dict[str, Any]:
    r={"tool":"WIFI_ESPECIALISTA Network Engineer Toolkit","version":VERSION,
       "collected_at_utc":datetime.now(timezone.utc).isoformat(),"system":system_info(),
       "interfaces":interface_inventory(),"routes":route_inventory(),"neighbors":passive_neighbors()}
    if include_wifi: r["wifi"]=wifi_inventory()
    return r

def write_report(data: dict[str, Any],output: str,fmt: str) -> Path:
    p=Path(output).expanduser(); p.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    def flatten(obj: Any,prefix: str="") -> None:
        if isinstance(obj,dict):
            for k,v in obj.items(): flatten(v,f"{prefix}{k}.")
        elif isinstance(obj,list):
            for i,v in enumerate(obj): flatten(v,f"{prefix}[{i}].")
        else: rows.append((prefix.rstrip("."),str(obj)))
    flatten(data)
    if fmt=="json": p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    elif fmt=="txt": p.write_text("\n".join(f"{k} = {v}" for k,v in rows)+"\n",encoding="utf-8")
    elif fmt=="csv":
        with p.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["field","value"]); w.writerows(rows)
    else: raise DiagnosticError("Format must be json, txt, or csv")
    return p

def emit(data: Any) -> None: print(json.dumps(data,indent=2,ensure_ascii=False))

def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="wifi-engineer",description="Cross-platform network diagnostics; read-only by default")
    p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}")
    s=p.add_subparsers(dest="action",required=True)
    for name,helptext in [("system","Host/runtime information"),("interfaces","Network interfaces"),
                          ("routes","Routing table"),("wifi","Wi-Fi details"),("neighbors","Passive ARP/neighbor cache")]:
        s.add_parser(name,help=helptext)
    x=s.add_parser("ipcalc",help="IPv4/IPv6 subnet calculations"); x.add_argument("address")
    x=s.add_parser("dns",help="System DNS resolution"); x.add_argument("hostname"); x.add_argument("--type",choices=["A","AAAA","ALL"],default="ALL")
    x=s.add_parser("ping",help="Bounded ICMP echo"); x.add_argument("host"); x.add_argument("--count",type=int,default=4); x.add_argument("--timeout",type=float,default=3)
    x=s.add_parser("trace",help="Route trace"); x.add_argument("host"); x.add_argument("--max-hops",type=int,default=20)
    x=s.add_parser("tcp-check",help="One TCP connection check to an authorized host"); x.add_argument("host"); x.add_argument("port",type=int); x.add_argument("--timeout",type=float,default=3)
    x=s.add_parser("report",help="Read-only baseline report"); x.add_argument("--format",choices=["json","txt","csv"],default="json"); x.add_argument("--output",default="network-report.json"); x.add_argument("--no-wifi",action="store_true")
    return p

def main(argv: list[str]|None=None) -> int:
    p=build_parser(); a=p.parse_args(argv)
    try:
        actions={"system":system_info,"interfaces":interface_inventory,"routes":route_inventory,
                 "wifi":wifi_inventory,"neighbors":passive_neighbors}
        if a.action in actions: emit(actions[a.action]()); return 0
        if a.action=="ipcalc": emit(calculate_network(a.address))
        elif a.action=="dns": emit(resolve_dns(a.hostname,a.type))
        elif a.action=="ping": emit(ping_host(a.host,a.count,a.timeout))
        elif a.action=="trace": emit(trace_route(a.host,a.max_hops))
        elif a.action=="tcp-check": emit(tcp_check(a.host,a.port,a.timeout))
        elif a.action=="report":
            path=write_report(collect_report(not a.no_wifi),a.output,a.format); print(f"Report saved: {path}")
        return 0
    except DiagnosticError as e:
        print(f"ERROR: {e}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
