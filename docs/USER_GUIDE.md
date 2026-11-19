# User Guide — Network Engineer Toolkit

## Requirements
- Python 3.10 or newer.
- Linux or Windows; macOS best-effort.
- Native tools: Linux ip, Windows ipconfig/route/netsh, ping; traceroute on Linux/macOS.
- Linux Wi-Fi: nmcli (preferred) or iw.
- No pip dependencies in v0.1.0.

## Quick start (Linux)
    python3 scripts/wifi_engineer.py --help
    python3 scripts/wifi_engineer.py system
    python3 scripts/wifi_engineer.py interfaces
    python3 scripts/wifi_engineer.py routes
    python3 scripts/wifi_engineer.py wifi
    python3 scripts/wifi_engineer.py neighbors

## Quick start (Windows PowerShell)
    py -3 scripts/wifi_engineer.py --help
    py -3 scripts/wifi_engineer.py system
    py -3 scripts/wifi_engineer.py interfaces
    py -3 scripts/wifi_engineer.py routes
    py -3 scripts/wifi_engineer.py wifi
    py -3 scripts/wifi_engineer.py neighbors

## IP, DNS, and connectivity
    python3 scripts/wifi_engineer.py ipcalc 192.168.10.14/24
    python3 scripts/wifi_engineer.py ipcalc 2001:db8::10/64
    python3 scripts/wifi_engineer.py dns example.com --type ALL
    python3 scripts/wifi_engineer.py ping 1.1.1.1 --count 4 --timeout 2
    python3 scripts/wifi_engineer.py trace example.com --max-hops 20
    python3 scripts/wifi_engineer.py tcp-check 192.0.2.10 443 --timeout 3

TCP check attempts one connection to exactly the host and port supplied. Only test authorized endpoints.

## Reports
    python3 scripts/wifi_engineer.py report --format json --output reports/baseline.json
    python3 scripts/wifi_engineer.py report --format txt --output reports/baseline.txt
    python3 scripts/wifi_engineer.py report --format csv --output reports/baseline.csv
    python3 scripts/wifi_engineer.py report --no-wifi --output reports/baseline-no-wifi.json

Reports can contain hostnames, IP/MAC addresses, interface names, and wireless identifiers. Review and sanitize before sharing.

## Tests
    python -m unittest discover -s tests -v

## Exit codes
- 0: command completed.
- 2: invalid input or diagnostic error.
- Native command failures are returned as structured output.
