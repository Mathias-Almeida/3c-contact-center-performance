CREATE TABLE fact_agent_interval (
    agent_interval_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    interval_key SMALLINT NOT NULL,

    agent_key INTEGER NOT NULL,
    team_key SMALLINT NOT NULL,
    skill_key SMALLINT NOT NULL,

    schedule_key BIGINT,

    operational_status VARCHAR(30) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,

    scheduled_flag BOOLEAN NOT NULL,
    present_flag BOOLEAN NOT NULL,
    available_flag BOOLEAN NOT NULL,
    productive_flag BOOLEAN NOT NULL,

    scheduled_minutes SMALLINT NOT NULL,

    planned_pause_minutes SMALLINT NOT NULL DEFAULT 0,
    unplanned_pause_minutes SMALLINT NOT NULL DEFAULT 0,

    training_minutes SMALLINT NOT NULL DEFAULT 0,
    meeting_minutes SMALLINT NOT NULL DEFAULT 0,
    coaching_minutes SMALLINT NOT NULL DEFAULT 0,
    administrative_minutes SMALLINT NOT NULL DEFAULT 0,
    technical_issue_minutes SMALLINT NOT NULL DEFAULT 0,

    -- Valores operacionais após a reconciliação de ausências
    absence_minutes SMALLINT NOT NULL DEFAULT 0,
    available_minutes SMALLINT NOT NULL DEFAULT 0,
    productive_minutes SMALLINT NOT NULL DEFAULT 0,

    -- Valores originais preservados antes da reconciliação
    available_minutes_before_absence SMALLINT NOT NULL,
    productive_minutes_before_absence SMALLINT NOT NULL,

    handling_seconds INTEGER NOT NULL DEFAULT 0,
    contacts_handled INTEGER NOT NULL DEFAULT 0,

    created_date DATE NOT NULL,

    CONSTRAINT fk_agent_interval_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_agent_interval_interval
        FOREIGN KEY (interval_key)
        REFERENCES dim_interval(interval_key),

    CONSTRAINT fk_agent_interval_agent
        FOREIGN KEY (agent_key)
        REFERENCES dim_agent(agent_key),

    CONSTRAINT fk_agent_interval_team
        FOREIGN KEY (team_key)
        REFERENCES dim_team(team_key),

    CONSTRAINT fk_agent_interval_skill
        FOREIGN KEY (skill_key)
        REFERENCES dim_skill(skill_key),

    CONSTRAINT fk_agent_interval_schedule
        FOREIGN KEY (schedule_key)
        REFERENCES fact_schedule(schedule_key),

    CONSTRAINT chk_agent_interval_status
        CHECK (
            operational_status IN (
                'Trabalhando',
                'Indisponível',
                'Ausente',
                'Folga'
            )
        ),

    CONSTRAINT chk_agent_interval_activity
        CHECK (
            activity_type IN (
                'Atendimento',
                'Pausa Planejada',
                'Pausa Particular',
                'Treinamento',
                'Reunião',
                'Coaching',
                'Administrativo',
                'Problema Técnico',
                'Ausente',
                'Folga'
            )
        ),

    CONSTRAINT chk_agent_interval_scheduled_minutes
        CHECK (
            scheduled_minutes >= 0
            AND scheduled_minutes <= 30
        ),

    CONSTRAINT chk_agent_interval_planned_pause
        CHECK (planned_pause_minutes >= 0),

    CONSTRAINT chk_agent_interval_unplanned_pause
        CHECK (unplanned_pause_minutes >= 0),

    CONSTRAINT chk_agent_interval_training
        CHECK (training_minutes >= 0),

    CONSTRAINT chk_agent_interval_meeting
        CHECK (meeting_minutes >= 0),

    CONSTRAINT chk_agent_interval_coaching
        CHECK (coaching_minutes >= 0),

    CONSTRAINT chk_agent_interval_administrative
        CHECK (administrative_minutes >= 0),

    CONSTRAINT chk_agent_interval_technical
        CHECK (technical_issue_minutes >= 0),

    CONSTRAINT chk_agent_interval_absence
        CHECK (
            absence_minutes >= 0
            AND absence_minutes <= scheduled_minutes
        ),

    CONSTRAINT chk_agent_interval_available
        CHECK (
            available_minutes >= 0
            AND available_minutes <= scheduled_minutes
        ),

    CONSTRAINT chk_agent_interval_productive
        CHECK (
            productive_minutes >= 0
            AND productive_minutes <= available_minutes
        ),

    CONSTRAINT chk_agent_interval_available_before_absence
        CHECK (
            available_minutes_before_absence >= 0
            AND available_minutes_before_absence <= scheduled_minutes
        ),

    CONSTRAINT chk_agent_interval_productive_before_absence
        CHECK (
            productive_minutes_before_absence >= 0
            AND productive_minutes_before_absence
                <= available_minutes_before_absence
        ),

    CONSTRAINT chk_agent_interval_handling
        CHECK (handling_seconds >= 0),

    CONSTRAINT chk_agent_interval_contacts
        CHECK (contacts_handled >= 0),

    CONSTRAINT uq_agent_interval_grain
        UNIQUE (
            date_key,
            interval_key,
            agent_key
        )
);