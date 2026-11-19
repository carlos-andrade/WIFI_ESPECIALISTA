# Architecture — Network Engineer Toolkit

## Objective
CLI cross-platform for network inventory and routine diagnostics. Version 0.1.0 prioritizes read-only inspection and explicitly requested bounded probes.

## Runtime
- Python 3.10+; standard library only.
- Linux and Windows are primary targets; macOS is best-effort.
- Tests use unittest.

## Initial components
- Host/runtime inventory.
- Network interface and route inventory using native OS commands.
- Wi-Fi details using netsh, nmcli/iw, or macOS airport utility.
- IPv4/IPv6 CIDR calculations.
- System DNS resolver (A, AAAA, ALL).
- Bounded ICMP ping and traceroute.
- Single-target/single-port TCP reachability test.
- Passive local ARP/neighbor cache inspection.
- JSON, TXT, and CSV baseline reports.

## Safety controls
1. Read-only inspection is the default.
2. Active probes require an explicit host.
3. TCP check attempts one port only; no port-range enumeration.
4. Ping count, timeout, and traceroute hops are bounded.
5. No shell execution, network configuration changes, credential collection, packet interception, or subnet-wide active discovery.
6. Use only on networks and systems for which authorization exists.

## Known limitations
- Interface, route, and Wi-Fi outputs are native command text, not normalized schemas.
- DNS uses the system resolver and does not query arbitrary DNS servers or non-address record types.
- ICMP and route tracing depend on OS tools, permissions, and firewall policy.
- Throughput measurement, SNMP, LLDP/CDP, NetFlow/IPFIX, packet capture, active discovery, vendor APIs, and Zabbix integration are future modules, not current features.

## Extension process
Each new module must have an approved requirement, permission model, supported-platform matrix, automated tests, and user documentation before implementation.
