CREATE TABLE dim_supervisor (
    supervisor_key SMALLSERIAL PRIMARY KEY,
    supervisor_code VARCHAR(20) NOT NULL UNIQUE,
    supervisor_name VARCHAR(100) NOT NULL,
    supervisor_email VARCHAR(150) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL
);