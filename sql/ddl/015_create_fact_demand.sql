CREATE TABLE fact_demand (
    demand_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    interval_key SMALLINT NOT NULL,
    skill_key SMALLINT NOT NULL,

    volume_offered INTEGER NOT NULL,
    volume_answered INTEGER NOT NULL,
    volume_abandoned INTEGER NOT NULL,

    aht_seconds INTEGER NOT NULL,
    workload_seconds BIGINT NOT NULL,

    asa_seconds INTEGER NOT NULL,

    sla_target NUMERIC(5,4) NOT NULL,
    service_level NUMERIC(5,4) NOT NULL,

    created_date DATE NOT NULL,

    CONSTRAINT fk_demand_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_demand_interval
        FOREIGN KEY (interval_key)
        REFERENCES dim_interval(interval_key),

    CONSTRAINT fk_demand_skill
        FOREIGN KEY (skill_key)
        REFERENCES dim_skill(skill_key),

    CONSTRAINT chk_demand_volume_offered
        CHECK (volume_offered >= 0),

    CONSTRAINT chk_demand_volume_answered
        CHECK (volume_answered >= 0),

    CONSTRAINT chk_demand_volume_abandoned
        CHECK (volume_abandoned >= 0),

    CONSTRAINT chk_demand_volume_balance
        CHECK (
            volume_answered + volume_abandoned <= volume_offered
        ),

    CONSTRAINT chk_demand_aht
        CHECK (aht_seconds > 0),

    CONSTRAINT chk_demand_workload
        CHECK (workload_seconds >= 0),

    CONSTRAINT chk_demand_asa
        CHECK (asa_seconds >= 0),

    CONSTRAINT chk_demand_sla_target
        CHECK (
            sla_target >= 0
            AND sla_target <= 1
        ),

    CONSTRAINT chk_demand_service_level
        CHECK (
            service_level >= 0
            AND service_level <= 1
        ),

    CONSTRAINT uq_demand_grain
        UNIQUE (
            date_key,
            interval_key,
            skill_key
        )
);