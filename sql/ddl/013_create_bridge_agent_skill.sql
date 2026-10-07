CREATE TABLE bridge_agent_skill (
    agent_skill_key SERIAL PRIMARY KEY,
    agent_key INTEGER NOT NULL,
    skill_key SMALLINT NOT NULL,
    skill_level VARCHAR(30) NOT NULL DEFAULT 'Intermediário',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_agent_skill_agent
        FOREIGN KEY (agent_key)
        REFERENCES dim_agent(agent_key),

    CONSTRAINT fk_agent_skill_skill
        FOREIGN KEY (skill_key)
        REFERENCES dim_skill(skill_key),

    CONSTRAINT chk_agent_skill_dates
        CHECK (
            valid_to IS NULL
            OR valid_to >= valid_from
        ),

    CONSTRAINT chk_agent_skill_level
        CHECK (
            skill_level IN (
                'Iniciante',
                'Intermediário',
                'Avançado',
                'Especialista'
            )
        ),

    CONSTRAINT uq_agent_skill
        UNIQUE (agent_key, skill_key)
);