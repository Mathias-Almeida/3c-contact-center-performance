CREATE TABLE dim_interval (
    interval_key SMALLINT PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    interval_label VARCHAR(20) NOT NULL,
    hour SMALLINT NOT NULL,
    minute SMALLINT NOT NULL
);