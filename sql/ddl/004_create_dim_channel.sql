CREATE TABLE dim_channel (
    channel_key SMALLSERIAL PRIMARY KEY,
    channel_code VARCHAR(20) NOT NULL UNIQUE,
    channel_name VARCHAR(50) NOT NULL,
    channel_description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL
);