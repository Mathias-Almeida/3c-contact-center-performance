## dim_organization

Tabela responsável por representar a estrutura hierárquica da organização do Contact Center.

Cada registro representa uma unidade organizacional, como Diretoria, Superintendência, Gerência ou Coordenação.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| organization_key | SMALLINT | Sim | Chave substituta utilizada internamente pelo banco de dados. |
| organization_code | VARCHAR(20) | Sim | Código de negócio da unidade organizacional. Exemplos: DIR001, SINT001, GER001 e COO001. |
| organization_name | VARCHAR(100) | Sim | Nome da unidade organizacional. |
| organization_level | VARCHAR(30) | Sim | Nível hierárquico da unidade: Diretoria, Superintendência, Gerência ou Coordenação. |
| parent_organization_key | SMALLINT | Não | Chave da unidade organizacional imediatamente superior. Permite representar a hierarquia por meio de uma referência à própria tabela. |
| is_active | BOOLEAN | Sim | Indica se a unidade organizacional está ativa. |
| created_date | DATE | Sim | Data de criação do registro. |

### Regra hierárquica

A coluna `parent_organization_key` referencia `organization_key` da própria `dim_organization`.

Para a unidade de maior nível, a Diretoria, o campo permanece `NULL`.

Exemplo:

```text
DIR001
└── SINT001
    └── GER001
        └── COO001