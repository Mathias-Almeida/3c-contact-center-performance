CREATE TABLE dim_operation (
    operation_key SMALLSERIAL PRIMARY KEY,
    operation_code VARCHAR(20) NOT NULL UNIQUE,
    operation_name VARCHAR(100) NOT NULL,
    operation_description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL
);