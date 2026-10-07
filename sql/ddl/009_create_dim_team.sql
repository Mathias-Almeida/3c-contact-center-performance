CREATE TABLE dim_team (
    team_key SMALLSERIAL PRIMARY KEY,
    team_code VARCHAR(20) NOT NULL UNIQUE,
    team_name VARCHAR(100) NOT NULL,
    supervisor_key SMALLINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL,

    CONSTRAINT fk_team_supervisor
        FOREIGN KEY (supervisor_key)
        REFERENCES dim_supervisor(supervisor_key)
);