# Avaliação da Biblioteca SNMP — Prova de Conceito

**Projeto:** WIFI_ESPECIALISTA  
**Versão do documento:** 1.0  
**Data:** 2026-11-20  
**Estado:** Candidata aprovada exclusivamente para PoC isolada  
**Não é:** aprovação para produção, integração no CLI ou instalação no runtime principal.

## 1. Decisão registada

O responsável aprovou pysnmplib==6.0.0 como candidata para uma prova de conceito (PoC) isolada de SNMPv3 authPriv.

A distribuição PyPI chama-se pysnmplib; o projeto upstream é pysnmp/pysnmp. Não confundir com a distribuição pysnmp, que pode instalar uma linha/fork diferente. Não instalar ambas no mesmo ambiente.

## 2. Evidência pública consultada

Fontes consultadas em 2026-11-20:
- PyPI, versão 6.0.0: https://pypi.org/project/pysnmplib/6.0.0/
- Documentação oficial: https://pysnmp.github.io/pysnmp/stable/
- Repositório upstream: https://github.com/pysnmp/pysnmp
- Workflow de publicação associado à atestação 6.0.0: https://github.com/pysnmp/pysnmp/blob/5c79cd1c0e1bc5563b3a58a95bcdbe32fdb9ad9d/.github/workflows/publish-to-pypi.yml

Características declaradas pelo projeto/PyPI:
- Licença BSD-2-Clause.
- Implementação Python pura.
- Suporte declarado a Python 3.10+.
- Suporte SNMPv1/v2c/v3 na biblioteca; o WIFI_ESPECIALISTA deverá impor exclusivamente SNMPv3 authPriv.
- Suporte USM com algoritmos de autenticação e privacidade.
- Transporte UDP IPv4/IPv6.
- A distribuição instala PyASN1 e PyCryptodomex; PyCryptodomex é necessário para cifragem SNMPv3.
- O extra compile instala componentes para compilação dinâmica de MIBs e não é necessário para esta PoC inicial.

## 3. Integridade da distribuição e ressalva de supply chain

A versão 6.0.0 foi publicada em 2026-09-29 com Trusted Publishing e atestação de proveniência PyPI associada ao repositório pysnmp/pysnmp, commit 5c79cd1c0e1bc5563b3a58a95bcdbe32fdb9ad9d.

O PyPI assinala uma mudança de proveniência face à publicação anterior. A nova configuração usa o workflow .github/workflows/publish-to-pypi.yml. A existência de atestação é evidência positiva de origem, mas não equivale a auditoria de segurança do código.

O workflow consultado usa referências de Actions por tags (actions/checkout@v7, astral-sh/setup-uv@v7, actions/upload-artifact@v7, actions/download-artifact@v8 e pypa/gh-action-pypi-publish@release/v1), em vez de SHA imutável. Isto deve constar da análise de supply chain; não prova comprometimento, mas reduz a reprodutibilidade/imutabilidade da cadeia de build.

Checksum publicado para o wheel pysnmplib-6.0.0-py3-none-any.whl:
- SHA-256: 8e97c6ec79669236994bb9b5cbd720577eae1af3603f0d178953b60250c2744d

O checksum deve ser revalidado diretamente contra o artefacto obtido no momento da PoC. Não descarregar nem instalar artefactos nesta fase documental.

## 4. Dependências e política de instalação da PoC

Dependência direta candidata, a fixar exclusivamente no ambiente isolado da PoC:

    pysnmplib==6.0.0

Dependências transitivas a inventariar e fixar com hashes no lockfile da PoC:
- PyASN1 (codec ASN.1).
- PyCryptodomex (primitivas criptográficas necessárias para privacidade SNMPv3).

Regras:
- Não adicionar pysnmplib ao requirements principal, pyproject principal ou runtime do CLI.
- Não instalar o extra compile nesta fase.
- Não instalar simultaneamente pysnmp e pysnmplib.
- Gerar lockfile reproduzível, com versões transitivas e hashes, após validar metadados oficiais.
- Verificar licenças e vulnerabilidades conhecidas de todas as dependências antes da PoC executável.
- Não armazenar credenciais de laboratório no repositório, ambiente CI ou fixtures.

## 5. Escopo da prova de conceito

A PoC deverá ficar isolada em diretório próprio (proposta: experiments/snmpv3_poc/) e não será importada pelo código de produção.

Objetivos técnicos:
1. Confirmar instalação e importação da distribuição exata pysnmplib==6.0.0 em ambiente virtual isolado.
2. Confirmar compatibilidade com Python 3.10, 3.11 e 3.12.
3. Efetuar somente SNMPv3 GET a um único host explicitamente fornecido.
4. Exigir security level authPriv; rejeitar qualquer outro nível antes de criar a sessão.
5. Solicitar username, authentication passphrase e privacy passphrase através de entrada oculta.
6. Não aceitar segredos como argumentos CLI, variáveis de ambiente, ficheiros de configuração ou opções de linha de comando.
7. Manter os segredos apenas em memória durante a operação e evitar persistência/cópias desnecessárias.
8. Sanitizar erros e garantir que segredos não surgem em stdout, stderr, logs, tracebacks ou relatórios.
9. Usar timeout e número de tentativas limitados; sem walk/bulk walk na primeira PoC.
10. Consultar apenas OIDs de identificação aprovados para o teste, sem descoberta de sub-redes ou varrimento.
11. Demonstrar que operações SET, SNMPv1 e SNMPv2c não são alcançáveis pela interface da PoC.
12. Testar com simulador/fixture local antes de qualquer equipamento real autorizado.

## 6. Fora de âmbito da PoC

- Integração no CLI principal.
- LLDP walk completo e inventário de interfaces.
- Polling, concorrência ou inventário em massa.
- SNMP SET, v1, v2c, broadcast, subnet discovery ou port scan.
- Compilação dinâmica de MIBs.
- Persistência de credenciais.
- Suporte a algoritmos criptográficos ainda não aprovados.
- Certificação de compatibilidade de produção.

## 7. Critérios de saída

A PoC só poderá recomendar adoção futura se apresentar:
- Matriz de execução Linux/Windows e Python 3.10–3.12.
- Evidência da versão efetivamente importada em runtime.
- Inventário de dependências e respetivas licenças.
- Verificação de hashes e proveniência do artefacto.
- Testes automatizados de prompt oculto e não exposição de segredos.
- Testes de autenticação falhada, timeout, resposta inválida e OID não suportado.
- Evidência de que apenas authPriv é utilizado e de que não há fallback v1/v2c.
- Revisão do código e da cadeia de dependências.
- Relatório de limitações e decisão formal de continuar ou rejeitar a biblioteca.

## 8. Decisões ainda pendentes

- Algoritmos concretos de autenticação e privacidade a suportar.
- MIBs/OIDs da primeira implementação.
- Parâmetros máximos de timeout, retries, resposta e rate limit.
- Estratégia final de simulador/fixtures.
- Aprovação final da biblioteca para eventual integração no produto.

**Conclusão:** pysnmplib==6.0.0 está aprovada apenas para avaliação técnica isolada. Não está aprovada para produção. A PoC não deve ser confundida com a implementação do módulo SNMP/LLDP.
