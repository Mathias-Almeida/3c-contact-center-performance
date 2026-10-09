-- ============================================================
-- 3C — Contact Center Performance Analytics
-- Tabela fato: fact_absence
-- Grão: uma linha por ocorrência de ausência
-- Origem: dados sintéticos
-- ============================================================

CREATE TABLE fact_absence (
    absence_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    agent_key INTEGER NOT NULL,
    absence_type_key SMALLINT NOT NULL,
    schedule_key BIGINT,

    absence_start_datetime TIMESTAMP NOT NULL,
    absence_end_datetime TIMESTAMP NOT NULL,

    -- Duração total da ocorrência, em minutos
    absence_minutes SMALLINT NOT NULL,

    created_date DATE NOT NULL,

    CONSTRAINT fk_absence_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_absence_agent
        FOREIGN KEY (agent_key)
        REFERENCES dim_agent(agent_key),

    CONSTRAINT fk_absence_type
        FOREIGN KEY (absence_type_key)
        REFERENCES dim_absence_type(absence_type_key),

    CONSTRAINT fk_absence_schedule
        FOREIGN KEY (schedule_key)
        REFERENCES fact_schedule(schedule_key),

    CONSTRAINT chk_absence_datetime
        CHECK (
            absence_end_datetime > absence_start_datetime
        ),

    CONSTRAINT chk_absence_minutes
        CHECK (
            absence_minutes > 0
            AND absence_minutes <= 1440
        )
);

-- Índices para consultas analíticas e reconciliação

CREATE INDEX idx_fact_absence_date
    ON fact_absence(date_key);

CREATE INDEX idx_fact_absence_agent_date
    ON fact_absence(agent_key, date_key);

CREATE INDEX idx_fact_absence_type
    ON fact_absence(absence_type_key);

CREATE INDEX idx_fact_absence_schedule
    ON fact_absence(schedule_key);