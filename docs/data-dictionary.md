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

## fact_absence — Ocorrências de ausência

**Descrição:** tabela fato que registra ocorrências sintéticas de ausência dos agentes, vinculadas às escalas planejadas, aos tipos de ausência e às datas operacionais.

**Grão:** uma ocorrência de ausência de um agente em uma data operacional.

**Volume inicial:** 43.793 ocorrências.

**Principais relacionamentos:**
- `date_key` → `dim_date`
- `agent_key` → `dim_agent`
- `absence_type_key` → `dim_absence_type`
- `schedule_key` → `fact_schedule`

**Principais atributos:**
- `absence_start_datetime`: início da ocorrência.
- `absence_end_datetime`: término da ocorrência.
- `absence_minutes`: duração da ocorrência em minutos.
- `absence_type_key`: classificação da ausência.
- `schedule_key`: escala relacionada à ocorrência.

**Regras de negócio:**
1. As ocorrências são geradas por simulação e não representam dados reais de colaboradores.
2. As ocorrências são vinculadas a escalas para identificar o período de trabalho potencialmente afetado.
3. A duração deve ser positiva e não pode ultrapassar 1.440 minutos por registro.
4. O impacto no indicador de absenteísmo deve respeitar a classificação do tipo de ausência em `dim_absence_type`.
5. Os minutos de ausência deverão ser conciliados com a execução intraday para evitar contabilizar capacidade como disponível durante períodos de ausência.
6. Férias, folgas, treinamentos e outros eventos não devem ser classificados automaticamente como faltas injustificadas.

**Observação de qualidade:** a carga inicial foi concluída com 43.793 ocorrências. A validação final de integridade e a conciliação com a execução intraday fazem parte das próximas etapas.