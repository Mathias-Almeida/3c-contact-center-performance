CREATE TABLE fact_schedule (
    schedule_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    agent_key INTEGER NOT NULL,
    team_key SMALLINT NOT NULL,
    shift_key SMALLINT NOT NULL,
    skill_key SMALLINT NOT NULL,

    schedule_status VARCHAR(30) NOT NULL,

    planned_start_datetime TIMESTAMP NOT NULL,
    planned_end_datetime TIMESTAMP NOT NULL,

    planned_minutes SMALLINT NOT NULL,
    scheduled_hours NUMERIC(5,2) NOT NULL,

    created_date DATE NOT NULL,

    CONSTRAINT fk_schedule_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_schedule_agent
        FOREIGN KEY (agent_key)
        REFERENCES dim_agent(agent_key),

    CONSTRAINT fk_schedule_team
        FOREIGN KEY (team_key)
        REFERENCES dim_team(team_key),

    CONSTRAINT fk_schedule_shift
        FOREIGN KEY (shift_key)
        REFERENCES dim_shift(shift_key),

    CONSTRAINT fk_schedule_skill
        FOREIGN KEY (skill_key)
        REFERENCES dim_skill(skill_key),

    CONSTRAINT chk_schedule_status
        CHECK (
            schedule_status IN (
                'Escalado'
            )
        ),

    CONSTRAINT chk_schedule_minutes
        CHECK (
            planned_minutes > 0
        ),

    CONSTRAINT chk_schedule_hours
        CHECK (
            scheduled_hours > 0
        ),

    CONSTRAINT chk_schedule_datetime
        CHECK (
            planned_end_datetime > planned_start_datetime
        ),

    CONSTRAINT uq_schedule_agent_date
        UNIQUE (
            agent_key,
            date_key
        )
);