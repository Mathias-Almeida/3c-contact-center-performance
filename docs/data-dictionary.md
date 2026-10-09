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

## `fact_agent_interval`

**Descrição:** tabela fato com granularidade de agente por intervalo operacional de 30 minutos.

**Finalidade:** registrar jornada programada, presença, disponibilidade, produtividade, atividades auxiliares e ausências dos agentes.

**Principais campos:**

- `date_key`: data operacional.
- `interval_key`: intervalo de 30 minutos.
- `agent_key`: agente.
- `team_key`: equipe.
- `skill_key`: habilidade operacional.
- `schedule_key`: jornada associada.
- `operational_status`: estado operacional do agente.
- `activity_type`: atividade predominante no intervalo.
- `scheduled_minutes`: minutos programados.
- `available_minutes`: minutos disponíveis após a reconciliação.
- `productive_minutes`: minutos produtivos após a reconciliação.
- `absence_minutes`: minutos de ausência sobrepostos ao intervalo.
- `available_minutes_before_absence`: disponibilidade original antes da reconciliação.
- `productive_minutes_before_absence`: produtividade original antes da reconciliação.
- `handling_seconds`: segundos de atendimento.
- `contacts_handled`: contatos atendidos.

**Regras de negócio:**

1. Cada registro representa um agente em uma data e intervalo operacional.
2. Os minutos de ausência são limitados aos minutos programados.
3. Disponibilidade e produtividade não podem ser negativas.
4. A produtividade não pode superar a disponibilidade.
5. Ausências integrais são identificadas pelo status `Ausente`.
6. Ausências parciais são registradas em `absence_minutes`, sem necessariamente substituir a atividade predominante.
7. A produtividade após a reconciliação é estimada proporcionalmente à disponibilidade restante.

**Premissa:** a reconciliação utiliza dados sintéticos e aproximações operacionais, não representando medições reais de um contact center.

## `fact_absence`

**Descrição:** tabela fato que registra ocorrências de ausência dos agentes.

**Grão:** uma linha por ocorrência de ausência.

**Principais campos:**

- `absence_key`: identificador da ocorrência.
- `date_key`: data de referência.
- `agent_key`: agente associado.
- `absence_type_key`: tipo de ausência.
- `schedule_key`: jornada associada, quando disponível.
- `absence_start_datetime`: início da ausência.
- `absence_end_datetime`: término da ausência.
- `absence_minutes`: duração da ocorrência em minutos.
- `created_date`: data de criação do registro.

**Relacionamentos:**

- `dim_date`
- `dim_agent`
- `dim_absence_type`
- `fact_schedule`

**Regras de negócio:**

1. O término deve ser posterior ao início.
2. A duração deve ser positiva e não superior a 1.440 minutos.
3. As ocorrências são relacionadas aos intervalos operacionais por jornada, data e sobreposição de horários.
4. A duração da ocorrência não deve ser somada diretamente aos minutos de ausência dos intervalos, pois representam granularidades diferentes.

**Volume registrado na carga atual:** 43.793 ocorrências.

**Origem:** dados sintéticos gerados para o projeto 3C. Os parâmetros utilizados não representam taxas reais de absenteísmo.