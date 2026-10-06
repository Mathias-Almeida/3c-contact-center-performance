# 3C — Contact Center Performance Analytics

Projeto de análise de desempenho operacional de um Contact Center fictício, desenvolvido com dados sintéticos e foco em **Workforce Management (WFM), planejamento operacional, indicadores de desempenho e Business Intelligence**.

O projeto simula a operação de um contact center multicanal localizado no Cariri, Ceará, permitindo analisar a relação entre **demanda, capacidade, força de trabalho e nível de serviço**.

> **Projeto educacional e de portfólio. Os dados utilizados são sintéticos e não representam uma operação real.**

---

## 🎯 Objetivo

Construir uma solução analítica capaz de transformar dados operacionais de um Contact Center em **indicadores, análises e insights para tomada de decisão**.

O projeto busca responder perguntas como:

- Qual é o volume de contatos recebido?
- Quais canais apresentam maior demanda?
- Quais são os períodos de maior pressão operacional?
- Como o AHT/TMA influencia o desempenho?
- Onde existe excesso ou insuficiência de capacidade?
- Quais intervalos apresentam risco de deterioração do SLA?
- Como a aderência dos agentes influencia a operação?
- Qual é o impacto do absenteísmo na capacidade?
- Quais operações e skills apresentam maior pressão?
- Quais decisões operacionais podem ser tomadas a partir dos indicadores?

---

## 🏢 Contexto da operação

O 3C — Cariri Contact Center representa uma operação de aproximadamente **5.000 agentes**, distribuídos entre diferentes canais, operações e skills.

### Canais

- Voice
- Chat
- WhatsApp
- E-mail / Backoffice

### Operações

- SAC
- Financeiro
- Retenção
- Suporte Técnico
- Vendas

Os agentes podem possuir mais de uma skill, permitindo representar uma operação **multiskill**.

---

## 📊 Principais indicadores

O projeto trabalhará com indicadores típicos de operações de Contact Center e WFM, incluindo:

### Demanda

- Volume recebido
- Volume atendido
- Volume abandonado
- Distribuição intraday
- Demanda por canal
- Demanda por skill

### Atendimento

- AHT / TMA
- ASA / TME
- SLA
- Taxa de abandono
- Occupancy

### Workforce

- Planned HC
- Scheduled HC
- Actual HC
- Required HC
- Adherence
- Absenteeism
- Availability
- Productive Hours
- Productivity

Os indicadores serão calculados a partir dos dados operacionais, buscando manter relações coerentes entre demanda, capacidade e desempenho.

---

## ⏱️ Granularidade

A análise intraday utiliza intervalos de **30 minutos**.

Um dia possui:

**48 intervalos de 30 minutos.**

Essa granularidade permite identificar períodos de pico, excesso de capacidade, falta de agentes e riscos de deterioração do SLA.

---

## 🗄️ Arquitetura de dados

O projeto utiliza uma arquitetura baseada em:

```text
Python / Pandas
       │
       ▼
Geração de dados sintéticos
       │
       ▼
PostgreSQL
       │
       ▼
SQL / Views / KPI Layer
       │
       ▼
Power BI
       │
       ▼
Análise operacional
```

### Tecnologias

- Python
- Pandas
- PostgreSQL
- SQL
- Power BI
- Git
- GitHub

---

## 🧱 Modelo de dados

O modelo está estruturado utilizando dimensões, fatos e tabelas de relacionamento.

### Dimensões

- `dim_date`
- `dim_interval`
- `dim_operation`
- `dim_channel`
- `dim_skill`
- `dim_supervisor`
- `dim_team`
- `dim_shift`
- `dim_agent`
- `dim_absence_type`

### Relacionamento

- `bridge_agent_skill`

### Fatos

- `fact_schedule`
- `fact_demand`
- `fact_agent_interval`
- `fact_absence`

---

## 📁 Estrutura do projeto

```text
3c-contact-center-performance/
│
├── README.md
├── .env
├── .gitignore
├── conexao_db.py
├── criar_estrutura.py
│
├── docs/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── src/
│   ├── generation/
│   ├── transformation/
│   ├── validation/
│   └── analytics/
│
├── sql/
│   ├── ddl/
│   ├── dimensions/
│   ├── facts/
│   ├── views/
│   └── kpis/
│
├── notebooks/
│
├── powerbi/
│
└── tests/
```

---

## 🚧 Status do projeto

O projeto está sendo desenvolvido de forma incremental.

### Concluído

- [x] Definição do contexto operacional
- [x] Definição dos principais KPIs
- [x] Definição da arquitetura de dados
- [x] Configuração do Python
- [x] Configuração do PostgreSQL
- [x] Configuração da conexão segura utilizando `.env`
- [x] Configuração do Git
- [x] Criação do repositório GitHub
- [x] Criação da `dim_date`
- [x] Criação da `dim_interval`
- [x] Criação da `dim_operation`

### Em desenvolvimento

- [ ] `dim_channel`
- [ ] `dim_skill`
- [ ] `dim_supervisor`
- [ ] `dim_team`
- [ ] `dim_shift`
- [ ] `dim_agent`
- [ ] `dim_absence_type`
- [ ] `bridge_agent_skill`
- [ ] `fact_schedule`
- [ ] `fact_demand`
- [ ] `fact_agent_interval`
- [ ] `fact_absence`
- [ ] Geração completa dos dados sintéticos
- [ ] Validação dos dados
- [ ] Camada analítica SQL
- [ ] KPIs
- [ ] Análises exploratórias
- [ ] Dashboard Power BI

---

## 🔬 Dados sintéticos

Os dados serão gerados artificialmente utilizando Python e Pandas.

A geração busca reproduzir comportamentos plausíveis de uma operação real, considerando fatores como:

- sazonalidade intraday;
- dia da semana;
- sazonalidade mensal;
- feriados;
- variação de demanda;
- variação de AHT;
- disponibilidade de agentes;
- absenteísmo;
- aderência;
- capacidade operacional;
- pressão sobre o SLA.

O objetivo não é gerar números aleatórios isolados, mas construir **relações operacionais coerentes entre as variáveis**.

---

## 📈 Roadmap

### Fase 1 — Data Foundation

- Modelagem dimensional
- PostgreSQL
- Dimensões
- Fatos
- Regras de negócio

### Fase 2 — Data Generation

- Geração de demanda
- Geração de workforce
- Geração de escalas
- Geração de absenteísmo
- Geração de indicadores operacionais

### Fase 3 — Analytics

- SQL
- Views analíticas
- Cálculo dos KPIs
- Validação estatística
- Análise exploratória

### Fase 4 — Business Intelligence

- Dashboard executivo
- Performance operacional
- Demanda
- Capacidade
- SLA
- Workforce
- Intraday Risk

### Fase 5 — WFM Analytics

- Forecast
- Capacity Planning
- Intraday Management
- Workforce Optimization
- Machine Learning aplicado a WFM

---

## 💡 Objetivo de portfólio

O projeto foi desenvolvido para demonstrar conhecimentos em:

**Data Analytics → SQL → Python → Workforce Management → Business Intelligence → Operational Decision Making**

Mais do que apresentar dashboards, o objetivo é demonstrar a capacidade de construir uma solução analítica desde a **modelagem e geração dos dados até a interpretação dos resultados e tomada de decisão operacional**.

---

## ⚠️ Observação

Este é um projeto de estudo e portfólio.

O 3C — Cariri Contact Center é uma organização fictícia e todos os dados operacionais são sintéticos.