# WIFI_ESPECIALISTA

Ferramentas profissionais para diagnóstico, inventário e apoio à engenharia de redes de computadores.

## Estado
- Núcleo inicial: Network Engineer Toolkit v0.1.0.
- Plataformas: Linux e Windows; macOS best-effort.
- Interface: CLI.
- Runtime: Python 3.10+.
- Padrão: diagnóstico seguro, relatórios e testes automatizados.

## Início rápido
    python3 scripts/wifi_engineer.py --help
    python3 scripts/wifi_engineer.py report --format json --output reports/baseline.json

No Windows, use py -3 se python3 não estiver disponível.

## Documentação
- docs/ARCHITECTURE.md
- docs/USER_GUIDE.md
- scripts/README.md
- GOVERNANCA/CHAT_OPERATIONS_POLICY.md

## Testes
    python -m unittest discover -s tests -v

## Segurança
Execute diagnósticos apenas em redes e sistemas sob sua administração ou com autorização explícita. Relatórios podem conter informação operacional sensível.

## Licença
MIT. Consulte LICENSE.
