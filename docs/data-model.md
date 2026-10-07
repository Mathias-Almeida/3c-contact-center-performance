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

## dim_shift

### Objetivo

A `dim_shift` representa as jornadas de trabalho disponíveis na operação do Contact Center.

A dimensão foi modelada para permitir diferentes horários de entrada e diferentes durações de jornada, refletindo a flexibilidade normalmente encontrada em operações de atendimento e Workforce Management (WFM).

### Granularidade

**1 linha = 1 jornada de trabalho possível.**

Cada registro representa uma combinação entre:

- horário de entrada;
- duração da jornada;
- horário de saída;
- tipo de jornada.

A tabela não representa a escala de um agente em um determinado dia. A associação entre um agente, uma data e uma jornada será realizada posteriormente pela `fact_schedule`.

### Estrutura

| Campo | Tipo | Descrição |
|---|---|---|
| `shift_key` | SMALLSERIAL | Chave substituta da jornada |
| `shift_code` | VARCHAR(20) | Código único da jornada |
| `shift_name` | VARCHAR(100) | Nome descritivo da jornada |
| `start_time` | TIME | Horário de início |
| `end_time` | TIME | Horário de término |
| `duration_minutes` | SMALLINT | Duração da jornada em minutos |
| `shift_hours` | NUMERIC(4,2) | Duração da jornada em horas |
| `is_overnight` | BOOLEAN | Indica se a jornada ultrapassa a meia-noite |
| `shift_type` | VARCHAR(30) | Classificação da jornada |
| `is_active` | BOOLEAN | Indica se a jornada está ativa |
| `created_date` | DATE | Data de criação do registro |

### Regra de geração

A dimensão possui horários de entrada em intervalos de **10 minutos**, cobrindo todo o período de 24 horas.

São considerados 144 horários possíveis:

```text
00:00, 00:10, 00:20, ..., 23:40, 23:50
```

Para cada horário de entrada são consideradas quatro durações:

- 4 horas;
- 6 horas;
- 7 horas;
- 8 horas.

Portanto:

```text
144 horários × 4 durações = 576 jornadas
```

A dimensão contém inicialmente **576 registros**.

### Tipos de jornada

| Duração | `shift_type` |
|---:|---|
| 4 horas | Part-time |
| 6 horas | Intermediário |
| 7 horas | Intermediário |
| 8 horas | Integral |

### Jornadas overnight

Uma jornada é classificada como `is_overnight = TRUE` quando seu horário de término ocorre no dia seguinte ao horário de início.

Exemplo:

```text
Início: 18:00
Duração: 8 horas
Término: 02:00
is_overnight: TRUE
```

Jornadas que terminam antes ou exatamente no limite do mesmo dia permanecem como `is_overnight = FALSE`.

### Regra de utilização

A `dim_shift` representa **possibilidades de jornada**, e não a jornada efetivamente trabalhada por um agente.

A jornada efetivamente atribuída a cada agente em determinada data será registrada posteriormente na `fact_schedule`.

Isso permite que um mesmo agente tenha jornadas diferentes ao longo do tempo, sem alterar seu cadastro na `dim_agent`.

### Relação com outras tabelas

```text
dim_shift
    ↓
fact_schedule
    ↓
dim_agent
```

A `fact_schedule` utilizará `shift_key` para identificar a jornada planejada de cada agente em determinado período.

### Observação de modelagem

A granularidade de entrada da jornada é de **10 minutos**, enquanto os dados operacionais intradiários da 3C utilizarão intervalos de **30 minutos**.

Essa diferença é intencional:

- **10 minutos:** maior flexibilidade para representar horários de entrada e saída;
- **30 minutos:** granularidade operacional utilizada para demanda, capacidade, aderência e demais indicadores intradiários.

Dessa forma, a dimensão de jornada possui maior precisão temporal sem aumentar desnecessariamente a granularidade das tabelas factuais operacionais.

## bridge_agent_skill

### Objetivo

A `bridge_agent_skill` representa os vínculos entre agentes e habilidades de atendimento.

A tabela foi criada porque um agente pode possuir mais de uma skill. Dessa forma, o relacionamento entre `dim_agent` e `dim_skill` é do tipo muitos-para-muitos, sendo necessária uma tabela associativa.

A bridge permite identificar:
- quais skills cada agente possui;
- qual é sua skill principal;
- quais são suas skills secundárias;
- o nível de proficiência em cada skill;
- o período de validade do vínculo.

### Granularidade

**1 linha = 1 vínculo entre um agente e uma skill.**

Um mesmo agente pode aparecer várias vezes na tabela, desde que esteja associado a skills diferentes.

Exemplo conceitual:

| Agente | Skill | Principal |
|---|---|---|
| AGT00001 | SAC Voice | Sim |
| AGT00001 | SAC Chat | Não |
| AGT00001 | SAC WhatsApp | Não |

Nesse exemplo, o agente possui três skills, mas apenas uma é considerada principal.

### Estrutura

| Campo | Tipo | Descrição |
|---|---|---|
| `agent_skill_key` | SERIAL | Chave substituta do vínculo |
| `agent_key` | INTEGER | Referência ao agente |
| `skill_key` | SMALLINT | Referência à skill |
| `skill_level` | VARCHAR(30) | Nível de proficiência |
| `is_primary` | BOOLEAN | Indica se é a skill principal do agente |
| `valid_from` | DATE | Data de início do vínculo |
| `valid_to` | DATE | Data de término do vínculo |
| `is_active` | BOOLEAN | Indica se o vínculo está ativo |

### Níveis de proficiência

Foram definidos quatro níveis:

- Iniciante
- Intermediário
- Avançado
- Especialista

A distribuição utilizada na geração sintética foi:

| Nível | Probabilidade |
|---|---:|
| Iniciante | 15% |
| Intermediário | 50% |
| Avançado | 30% |
| Especialista | 5% |

### Regra de associação com as operações

Os agentes recebem suas skills de acordo com a operação de sua equipe.

| Operação | Skill principal | Skills secundárias possíveis |
|---|---|---|
| SAC | V001 — SAC Voice | C001, W001, E001 |
| Financeiro | V002 — Financeiro Voice | W002 |
| Retenção | V003 — Retenção Voice | Nenhuma |
| Suporte Técnico | V004 — Suporte Técnico Voice | C002, W003 |
| Vendas | V005 — Vendas Voice | C003 |

Cada agente recebe obrigatoriamente uma skill principal.

Quando existem skills secundárias disponíveis:
- 60% de probabilidade de receber uma segunda skill;
- quando existem pelo menos duas opções secundárias, 20% de probabilidade de receber uma terceira skill.

A geração utiliza `SEED = 42`, garantindo reprodutibilidade dos dados sintéticos.

### Regras temporais

O vínculo entre agente e skill é iniciado na data de admissão do agente:

```text
valid_from = hire_date

## fact_schedule

### Objetivo

A tabela `fact_schedule` representa a escala planejada dos agentes do contact center ao longo do tempo.

Ela registra quais agentes foram escalados para trabalhar em determinada data, em qual equipe, em qual skill e em qual jornada de trabalho.

A tabela representa o planejamento operacional e não a presença efetiva do agente.

Dessa forma, `fact_schedule` é utilizada como base para análises de:

- Headcount escalado;
- cobertura operacional;
- horas planejadas;
- distribuição de jornadas;
- distribuição de skills;
- comparação entre capacidade planejada e demanda;
- aderência entre escala planejada e execução;
- planejamento de Workforce Management (WFM).

### Granularidade

> 1 registro = 1 agente escalado para 1 jornada de trabalho em 1 determinado dia.

Exemplo conceitual:

```text
Agente:       1250
Data:         15/03/2026
Equipe:       84
Shift:        327
Skill:        SAC Voice
Status:       Escalado