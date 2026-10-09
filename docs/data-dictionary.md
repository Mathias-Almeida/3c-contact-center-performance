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
        
## dim_team

Tabela responsável por representar as equipes operacionais do Contact Center.

Cada registro representa uma equipe operacional associada a um supervisor.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| team_key | SMALLINT | Sim | Chave substituta utilizada internamente pelo banco de dados. |
| team_code | VARCHAR(20) | Sim | Código de negócio da equipe. |
| team_name | VARCHAR(100) | Sim | Nome da equipe. |
| supervisor_key | SMALLINT | Sim | Chave do supervisor responsável pela equipe. Referencia `dim_supervisor.supervisor_key`. |
| is_active | BOOLEAN | Sim | Indica se a equipe está ativa. |
| created_date | DATE | Sim | Data de criação do registro. |

### Regra de relacionamento

No modelo inicial, cada supervisor está associado a uma equipe principal.

A relação é:

```text
Supervisor
   ↓
Equipe              

## fact_demand

### Objetivo

A tabela `fact_demand` representa a demanda operacional do contact center ao longo do tempo.

Ela registra o volume de contatos, o tempo médio de atendimento e indicadores relacionados à espera e ao nível de serviço para cada skill em cada intervalo operacional.

A tabela constitui a principal fonte de dados para representar a demanda que deverá ser atendida pela capacidade operacional do contact center.

### Granularidade

> 1 registro = 1 dia × 1 intervalo de 30 minutos × 1 skill.

Exemplo:

```text
Data:       15/03/2026
Intervalo:  10:30–11:00
Skill:      V001 - SAC Voice

## fact_agent_interval — Execução operacional intraday

**Descrição:** tabela fato que registra a execução operacional dos agentes em intervalos de 30 minutos. Permite comparar a escala planejada com a disponibilidade, as atividades e o tempo produtivo efetivamente registrados na operação.

**Grão:** um registro por agente, data operacional e intervalo de 30 minutos.

**Volume inicial:** 15.088.238 registros.

**Principais relacionamentos:**
- `date_key` → `dim_date`
- `interval_key` → `dim_interval`
- `agent_key` → `dim_agent`
- `team_key` → `dim_team`
- `skill_key` → `dim_skill`
- `schedule_key` → `fact_schedule`

**Principais indicadores e atributos:**
- `scheduled_minutes`: minutos previstos na escala dentro do intervalo.
- `planned_pause_minutes`: minutos de pausas planejadas.
- `unplanned_pause_minutes`: minutos de indisponibilidade não planejada.
- `available_minutes`: minutos disponíveis para a operação.
- `productive_minutes`: minutos classificados como produtivos.
- `handling_seconds`: tempo de atendimento atribuído ao agente.
- `contacts_handled`: quantidade de contatos tratados.
- `operational_status`: situação operacional do agente.
- `activity_type`: atividade predominante registrada no intervalo.

**Regras de negócio:**
1. O grão é controlado pela restrição de unicidade de `date_key`, `interval_key` e `agent_key`.
2. A escala planejada é obtida por meio de `schedule_key`, que referencia `fact_schedule`.
3. A jornada é identificada por meio de `fact_schedule` e `dim_shift`; a tabela não possui `shift_key` próprio.
4. Os minutos disponíveis não podem exceder os minutos escalados, e os minutos produtivos não podem exceder os disponíveis.
5. Os indicadores finais de aderência, ocupação, produtividade e shrinkage serão calculados na camada analítica, respeitando seus respectivos denominadores.
6. Os campos `handling_seconds` e `contacts_handled` permanecem zerados nesta etapa inicial e deverão ser conciliados com a distribuição da demanda em uma etapa posterior.

**Observação de qualidade:** a geração e a carga inicial foram concluídas com 15.088.238 registros, sem erros, e as validações de consistência foram aprovadas.