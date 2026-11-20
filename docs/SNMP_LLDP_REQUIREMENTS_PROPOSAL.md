# Proposta de Requisitos — Módulos SNMP e LLDP
**Documento:** PROPOSTA — não aprovado para implementação  
**Versão:** 1.2  
**Estado:** Requisitos parciais aprovados; decisões técnicas e revisão documental pendentes  
**Projeto:** WIFI_ESPECIALISTA

## 1. Objetivo

Definir os requisitos funcionais, de segurança, compatibilidade e aceitação para uma futura extensão do Network Engineer Toolkit com recolha controlada de inventário através de SNMP e descoberta de vizinhança através de LLDP.

Este documento não autoriza implementação, instalação de dependências, recolha de dados ou alterações à arquitetura existente. A implementação só poderá começar após aprovação expressa dos requisitos, seleção da biblioteca e validação das restantes decisões técnicas.

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
3. **SNMPv3 com autenticação e privacidade (authPriv) é o único nível SNMP admitido na primeira versão.**
4. SNMPv1 e SNMPv2c ficam excluídos da primeira versão. Não implementar fallback automático ou modo de compatibilidade para estes protocolos.
5. As credenciais SNMPv3 serão solicitadas interativamente através de prompt com entrada oculta, usando mecanismo equivalente a `getpass`.
6. As credenciais devem permanecer apenas em memória durante a consulta e ser descartadas após a sua conclusão. Não persistir credenciais entre execuções.
7. Credenciais, passphrases e material criptográfico não podem ser aceites como texto simples em argumentos CLI nem gravados no repositório, histórico de shell, relatórios, cache, stdout, stderr, logs ou mensagens de erro.
8. A interface não deve ecoar os segredos. Exceções e diagnósticos devem ser sanitizados para impedir exposição indireta.
9. Validar limites de timeout, tentativas, quantidade de OIDs e tamanho das respostas.
10. Não seguir automaticamente destinos, endereços ou referências fornecidos pelas respostas SNMP.
11. Consultas devem ser estritamente read-only e limitadas aos OIDs/MIBs aprovados.
12. O comportamento padrão deve falhar de forma segura perante timeout, autenticação inválida, resposta malformada ou equipamento não suportado.

## 4. Compatibilidade — matriz proposta

| Plataforma | SNMP | LLDP via SNMP | Estado |
|---|---|---|---|
| Linux | A validar | A validar | Alvo primário |
| Windows | A validar | A validar | Alvo primário |
| macOS | A validar | A validar | Best-effort |

A matriz final depende da biblioteca selecionada, do suporte a sockets UDP, da gestão segura de credenciais e da execução nos runners CI disponíveis. Não assumir paridade entre plataformas sem testes.

## 5. Biblioteca candidata e decisões técnicas ainda abertas

As decisões seguintes exigem revisão antes da implementação:

- Avaliação final da biblioteca SNMP, dependências, manutenção e compatibilidade multiplataforma após prova de conceito.
- Algoritmos SNMPv3 de autenticação e privacidade suportados pela biblioteca e compatibilidade com equipamentos-alvo.
- Lista inicial e versão dos MIBs/OIDs suportados.
- Estratégia de normalização dos resultados entre fabricantes.
- Política de timeout, retries, concorrência e rate limiting.
- Estratégia de testes com simuladores/fixtures sem depender de equipamentos reais.
- Licenciamento e distribuição das dependências.

**Decisões já aprovadas pelo responsável do projeto:**

- SNMPv1 e SNMPv2c excluídos da primeira versão; apenas SNMPv3 authPriv.
- Credenciais solicitadas por prompt interativo com entrada oculta (getpass), mantidas apenas em memória durante a consulta, sem persistência.

**Biblioteca aprovada apenas como candidata para prova de conceito isolada:** `pysnmplib==6.0.0` (distribuição PyPI; projeto upstream `pysnmp/pysnmp`). Esta aprovação não equivale a adoção em produção, não autoriza adicionar a dependência ao runtime principal e não autoriza integração no CLI. A prova de conceito deverá permanecer isolada e validar SNMPv3 authPriv, entrada oculta de credenciais, sanitização de erros e compatibilidade com Python 3.10+ em Linux e Windows. A dependência criptográfica necessária para privacidade deverá ser inspecionada e fixada explicitamente; não instalar extras de compilação MIB sem requisito separado.

## 6. Interface CLI proposta

Os nomes abaixo são ilustrativos e não constituem contrato final:

- `snmp system <host>`
- `snmp interfaces <host>`
- `lldp neighbors <host>`

Os comandos deverão exigir parâmetros explícitos e expor opções limitadas para timeout e tentativas. A recolha de credenciais deverá ocorrer por prompt oculto; nunca aceitar segredos em argumentos visíveis do processo.

Não implementar descoberta de sub-redes nem comandos com intervalos de IP.

## 7. Modelo de dados e relatórios

- Preservar a proveniência: equipamento consultado, instante UTC, versão do módulo, protocolo, MIB/OID e estado da consulta.
- Distinguir claramente valor ausente, OID não suportado, acesso negado, timeout e falha de autenticação.
- Normalizar campos comuns sem descartar os valores originais relevantes.
- Não incluir credenciais, passphrases, chaves ou material criptográfico nos relatórios.
- Evitar recolher dados de configuração que não sejam necessários ao inventário.

## 8. Testes e critérios de aceitação

A implementação futura só será elegível para integração quando:

1. Testes unitários cobrirem parsing, normalização, validação de entradas e erros.
2. Fixtures reproduzíveis cobrirem respostas válidas, incompletas, malformadas e OIDs não suportados.
3. Testes de segurança confirmarem que segredos não aparecem em stdout, stderr, logs, exceções ou relatórios.
4. Testes confirmarem que a entrada de credenciais não ecoa os segredos e que estes não são persistidos nem incluídos em argumentos CLI.
5. Testes verificarem limites de timeout, retries, OIDs e tamanho de resposta.
6. Testes confirmarem que não existe operação SNMP SET, SNMPv1, SNMPv2c nem descoberta de sub-redes.
7. CI cobrir Linux e Windows com Python 3.10, 3.11 e 3.12; macOS será incluído se houver runner e suporte aprovados.
8. A documentação explicar permissões, riscos, limitações, configuração segura e exemplos autorizados.
9. A licença de cada dependência for verificada e registada.
10. A arquitetura e o guia de utilização forem atualizados.
11. O Pull Request apresentar evidências de testes e revisão antes da integração.

## 9. Fora de âmbito

- SNMP SET ou configuração remota.
- SNMPv1 e SNMPv2c.
- Descoberta automática de redes/sub-redes.
- Varredura de portas ou serviços.
- CDP, NetFlow/IPFIX, sFlow ou captura de pacotes.
- Integração Zabbix, alertas ou monitorização contínua.
- Armazenamento central de credenciais.
- Dashboard ou interface gráfica.
- Inventário em massa ou polling recorrente.

Estes itens exigem requisitos e aprovação separados.

## 10. Estado de aprovação e próximos bloqueios

### 10.1 Decisões aprovadas

- [x] SNMP estritamente read-only.
- [x] LLDP limitado à leitura de tabelas via SNMP.
- [x] SNMPv3 authPriv como único protocolo/nível de segurança suportado na primeira versão.
- [x] Exclusão de SNMPv1 e SNMPv2c.
- [x] Credenciais por prompt interativo oculto (getpass), apenas em memória e sem persistência.

### 10.2 Decisões pendentes

- [x] Candidata para prova de conceito: `pysnmplib==6.0.0` (não aprovada para produção).
- [ ] Algoritmos de autenticação/privacidade SNMPv3 suportados.
- [ ] MIBs/OIDs iniciais e modelo de normalização.
- [ ] Matriz de plataformas comprovada por testes.
- [ ] Limites operacionais: timeout, retries, concorrência, rate limiting e tamanho máximo das respostas.
- [ ] Simuladores/fixtures e estratégia de testes.
- [ ] Revisão final e aprovação expressa do conjunto de requisitos.

**Estado final:** requisitos parcialmente aprovados e registados. Este documento continua a ser uma proposta; não autoriza implementação nem instalação de dependências.

## 11. Histórico de decisões

- **2026-11-20:** responsável aprovou SNMPv3 authPriv exclusivamente, excluindo SNMPv1 e SNMPv2c.
- **2026-11-20:** responsável aprovou recolha interativa de credenciais com entrada oculta (getpass), sem exposição em argumentos, logs ou relatórios e sem persistência.
- **2026-11-20:** versão 1.1 consolida documentalmente as decisões anteriores. A proposta continua sujeita às decisões pendentes e à revisão final.
- **2026-11-20:** responsável aprovou `pysnmplib==6.0.0` exclusivamente como candidata para prova de conceito isolada, sem adoção no runtime principal ou aprovação para produção.
- **2026-11-20:** versão 1.2 regista a aprovação limitada da biblioteca e define o escopo da prova de conceito.
