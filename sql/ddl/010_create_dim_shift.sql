CREATE TABLE dim_shift (
    shift_key SMALLSERIAL PRIMARY KEY,
    shift_code VARCHAR(20) NOT NULL UNIQUE,
    shift_name VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes SMALLINT NOT NULL,
    shift_hours NUMERIC(4,2) NOT NULL,
    is_overnight BOOLEAN NOT NULL DEFAULT FALSE,
    shift_type VARCHAR(30) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL
);