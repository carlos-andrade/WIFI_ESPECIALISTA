# Proposta de Requisitos — Módulos SNMP e LLDP
**Documento:** PROPOSTA — não aprovado para implementação  
**Versão:** 1.0  
**Estado:** Aguardando revisão e aprovação  
**Projeto:** WIFI_ESPECIALISTA

## 1. Objetivo

Definir os requisitos funcionais, de segurança, compatibilidade e aceitação para uma futura extensão do Network Engineer Toolkit com recolha controlada de inventário através de SNMP e descoberta de vizinhança através de LLDP.

Este documento não autoriza implementação, instalação de dependências, recolha de dados ou alterações à arquitetura existente. A implementação só poderá começar após aprovação expressa dos requisitos e das decisões técnicas em aberto.

## 2. Âmbito proposto

### 2.1 SNMP — leitura de informação

A primeira versão deverá limitar-se a operações de leitura em equipamentos explicitamente indicados pelo operador, com possibilidade de obter:

- Identificação do equipamento: sysName, sysDescr, sysObjectID e sysUpTime.
- Interfaces: ifName/ifDescr, ifAdminStatus, ifOperStatus, ifSpeed/ifHighSpeed e contadores de tráfego.
- Endereços e estado operacional, apenas quando expostos pelos MIBs suportados.
- Inventário resumido e exportação para os formatos de relatório já existentes, após validação do modelo de dados.

Não incluir escrita SNMP (SET), alteração de configuração, reinicialização, execução remota, descoberta automática de sub-redes ou varrimento de intervalos de endereços.

### 2.2 LLDP — vizinhos diretamente anunciados

A primeira versão deverá ler tabelas LLDP disponibilizadas pelo próprio equipamento via SNMP, quando suportadas:

- Identificador/chassis ID e respetivo subtipo.
- Port ID e subtipo.
- Nome e descrição da porta remota.
- System Name e System Description remotos.
- Capabilities anunciadas.
- Idade/TTL da informação, quando disponível.

A ausência de LLDP, de tabelas ou de permissões deverá ser apresentada como estado não disponível, nunca como prova de inexistência física de vizinhos.

CDP, descoberta por broadcast e protocolos proprietários ficam fora deste âmbito inicial.

## 3. Modelo de autorização e segurança

1. Cada consulta exige um endereço/hostname de destino explícito.
2. O operador deve ter autorização administrativa para consultar o equipamento.
3. SNMPv3 com autenticação e privacidade deve ser a opção preferencial.
4. SNMPv1 não será suportado na primeira versão.
5. O eventual suporte a SNMPv2c exige decisão expressa, aviso de segurança e mecanismo que não exponha community strings em argumentos de linha de comando, logs, relatórios ou histórico de shell.
6. Credenciais e segredos não podem ser gravados no repositório, relatórios, cache ou logs.
7. Não persistir credenciais entre execuções na primeira versão.
8. Validar limites de timeout, tentativas, quantidade de OIDs e tamanho das respostas.
9. Não seguir automaticamente destinos, endereços ou referências fornecidos pelas respostas SNMP.
10. Mensagens de erro devem evitar revelar segredos e dados de autenticação.
11. Consultas devem ser estritamente read-only e limitadas aos OIDs/MIBs aprovados.
12. O comportamento padrão deve falhar de forma segura perante timeout, autenticação inválida, resposta malformada ou equipamento não suportado.

## 4. Compatibilidade — matriz proposta

| Plataforma | SNMP | LLDP via SNMP | Estado |
|---|---|---|---|
| Linux | A validar | A validar | Alvo primário |
| Windows | A validar | A validar | Alvo primário |
| macOS | A validar | A validar | Best-effort |

A matriz final depende da biblioteca selecionada, do suporte a sockets UDP, da gestão segura de credenciais e da execução nos runners CI disponíveis. Não assumir paridade entre plataformas sem testes.

## 5. Decisões técnicas ainda abertas

As decisões seguintes exigem revisão antes da implementação:

- Biblioteca SNMP Python e respetiva licença, manutenção, dependências e compatibilidade com Python 3.10+.
- Suporte SNMPv3: algoritmos de autenticação/privacidade aceites e compatibilidade com equipamentos legados.
- Se SNMPv2c será excluído ou admitido como modo explicitamente inseguro.
- Forma de entrada de credenciais: prompt interativo, ficheiro de segredo externo com permissões restritas ou integração futura com gestor de segredos.
- Lista inicial e versão dos MIBs/OIDs suportados.
- Estratégia de normalização dos resultados entre fabricantes.
- Política de timeout, retries, concorrência e rate limiting.
- Estratégia de testes com simuladores/fixtures sem depender de equipamentos reais.
- Licenciamento e distribuição das dependências.

Nenhuma biblioteca ou abordagem é considerada aprovada por este documento.

## 6. Interface CLI proposta

Os nomes abaixo são ilustrativos e não constituem contrato final:

- `snmp system <host>`
- `snmp interfaces <host>`
- `lldp neighbors <host>`

Os comandos deverão exigir parâmetros explícitos e expor opções limitadas para timeout e tentativas. Credenciais nunca devem ser aceites como texto simples em argumentos visíveis do processo.

Não implementar descoberta de sub-redes nem comandos com intervalos de IP.

## 7. Modelo de dados e relatórios

- Preservar a proveniência: equipamento consultado, instante UTC, versão do módulo, protocolo, MIB/OID e estado da consulta.
- Distinguir claramente valor ausente, OID não suportado, acesso negado, timeout e falha de autenticação.
- Normalizar campos comuns sem descartar os valores originais relevantes.
- Não incluir credenciais, community strings, chaves ou material criptográfico nos relatórios.
- Evitar recolher dados de configuração que não sejam necessários ao inventário.

## 8. Testes e critérios de aceitação

A implementação futura só será elegível para integração quando:

1. Testes unitários cobrirem parsing, normalização, validação de entradas e erros.
2. Fixtures reproduzíveis cobrirem respostas válidas, incompletas, malformadas e OIDs não suportados.
3. Testes de segurança confirmarem que segredos não aparecem em stdout, stderr, logs, exceções ou relatórios.
4. Testes verificarem limites de timeout, retries, OIDs e tamanho de resposta.
5. Testes confirmarem que não existe operação SNMP SET nem descoberta de sub-redes.
6. CI cobrir Linux e Windows com Python 3.10, 3.11 e 3.12; macOS será incluído se houver runner e suporte aprovados.
7. A documentação explicar permissões, riscos, limitações, configuração segura e exemplos autorizados.
8. A licença de cada dependência for verificada e registada.
9. A arquitetura e o guia de utilização forem atualizados.
10. O Pull Request apresentar evidências de testes e revisão antes da integração.

## 9. Fora de âmbito

- SNMP SET ou configuração remota.
- Descoberta automática de redes/sub-redes.
- Varredura de portas ou serviços.
- CDP, NetFlow/IPFIX, sFlow ou captura de pacotes.
- Integração Zabbix, alertas ou monitorização contínua.
- Armazenamento central de credenciais.
- Dashboard ou interface gráfica.
- Inventário em massa ou polling recorrente.

Estes itens exigem requisitos e aprovação separados.

## 10. Aprovação necessária

Antes de iniciar implementação, o responsável pelo projeto deverá aprovar ou alterar expressamente:

- [ ] Âmbito SNMP read-only descrito na secção 2.1.
- [ ] Âmbito LLDP via tabelas SNMP descrito na secção 2.2.
- [ ] Política de segurança da secção 3.
- [ ] Decisão sobre SNMPv2c.
- [ ] Estratégia de credenciais.
- [ ] Biblioteca e licença.
- [ ] Matriz de plataformas.
- [ ] Critérios de aceitação da secção 8.

**Estado final:** proposta técnica submetida para revisão. Não iniciar implementação até existir aprovação documentada.
