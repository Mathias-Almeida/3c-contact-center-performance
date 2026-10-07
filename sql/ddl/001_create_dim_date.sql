CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year SMALLINT NOT NULL,
    day_of_month SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_name VARCHAR(100),
    is_business_day BOOLEAN NOT NULL
);