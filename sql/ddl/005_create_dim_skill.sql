CREATE TABLE dim_skill (
    skill_key SMALLSERIAL PRIMARY KEY,
    skill_code VARCHAR(20) NOT NULL UNIQUE,
    skill_name VARCHAR(100) NOT NULL,
    operation_key SMALLINT NOT NULL,
    channel_key SMALLINT NOT NULL,
    skill_description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL,

    CONSTRAINT fk_skill_operation
        FOREIGN KEY (operation_key)
        REFERENCES dim_operation(operation_key),

    CONSTRAINT fk_skill_channel
        FOREIGN KEY (channel_key)
        REFERENCES dim_channel(channel_key)
);