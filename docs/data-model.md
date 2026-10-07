## Dimensão Organizacional

A estrutura organizacional do 3C foi modelada de forma hierárquica por meio da tabela `dim_organization`.

A hierarquia representa os principais níveis de gestão do Contact Center:

Diretoria → Superintendência → Gerência → Coordenação

A tabela utiliza uma chave estrangeira autorreferenciada (`parent_organization_key`), permitindo que cada unidade organizacional aponte para sua unidade imediatamente superior.

### Estrutura organizacional

- 1 Diretoria
- 2 Superintendências
- 8 Gerências
- 20 Coordenações
- 31 unidades organizacionais no total

A estrutura atual é:

Diretoria de Operações
- Superintendência de Operações
  - Gerência de SAC
  - Gerência Financeira
  - Gerência de Retenção
  - Gerência Comercial
- Superintendência Digital e Suporte
  - Gerência de Suporte Técnico
  - Gerência de Canais Digitais
  - Gerência de Backoffice
  - Gerência de Performance Operacional

As gerências são subdivididas em 20 coordenações.

### Autorreferência da organização

A coluna `parent_organization_key` referencia a própria `dim_organization`.

Exemplo:

DIR001
→ SINT001
→ GER001
→ COO001

Dessa forma, a hierarquia não depende de colunas fixas para cada nível organizacional e pode ser expandida futuramente.

## Relacionamento entre Supervisor e Organização

A tabela `dim_supervisor` possui a coluna `organization_key`, que referencia `dim_organization`.

Nesse modelo, cada supervisor é associado a uma Coordenação.

A estrutura organizacional passa a ser:

Diretoria
→ Superintendência
→ Gerência
→ Coordenação
→ Supervisor

Inicialmente, os 220 supervisores são distribuídos entre as 20 coordenações, resultando em 11 supervisores por coordenação.