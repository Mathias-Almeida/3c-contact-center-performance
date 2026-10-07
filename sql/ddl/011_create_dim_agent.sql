CREATE TABLE dim_agent (
    agent_key SERIAL PRIMARY KEY,
    agent_code VARCHAR(20) NOT NULL UNIQUE,
    agent_name VARCHAR(150) NOT NULL,
    agent_email VARCHAR(150) NOT NULL UNIQUE,
    team_key SMALLINT NOT NULL,
    hire_date DATE NOT NULL,
    termination_date DATE,
    agent_status VARCHAR(30) NOT NULL,
    employment_type VARCHAR(30) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL,

    CONSTRAINT fk_agent_team
        FOREIGN KEY (team_key)
        REFERENCES dim_team(team_key),

    CONSTRAINT chk_agent_dates
        CHECK (
            termination_date IS NULL
            OR termination_date >= hire_date
        ),

    CONSTRAINT chk_agent_status
        CHECK (
            agent_status IN (
                'Ativo',
                'Afastado',
                'Desligado'
            )
        ),

    CONSTRAINT chk_employment_type
        CHECK (
            employment_type IN (
                'CLT',
                'Temporário',
                'Aprendiz'
            )
        )
);