INSERT INTO dim_shift (
    shift_code,
    shift_name,
    start_time,
    end_time,
    duration_minutes,
    shift_hours,
    is_overnight,
    shift_type,
    is_active,
    created_date
)
SELECT
    'SHIFT_' ||
    TO_CHAR(start_time, 'HH24MI') ||
    '_' ||
    duration_hours || 'H' AS shift_code,

    'Turno ' ||
    TO_CHAR(start_time, 'HH24:MI') ||
    ' - ' ||
    duration_hours || 'h' AS shift_name,

    start_time,

    (
        start_time + (duration_hours * INTERVAL '1 hour')
    )::TIME AS end_time,

    duration_hours * 60 AS duration_minutes,

    duration_hours::NUMERIC(4,2) AS shift_hours,

    (
        start_time + (duration_hours * INTERVAL '1 hour')
    )::TIME < start_time AS is_overnight,

    CASE
        WHEN duration_hours = 4 THEN 'Part-time'
        WHEN duration_hours IN (6, 7) THEN 'Intermediário'
        WHEN duration_hours = 8 THEN 'Integral'
    END AS shift_type,

    TRUE AS is_active,

    DATE '2026-01-01' AS created_date

FROM
    generate_series(
        0,
        143
    ) AS intervals(interval_number)

CROSS JOIN
    (
        VALUES
            (4),
            (6),
            (7),
            (8)
    ) AS durations(duration_hours)

CROSS JOIN LATERAL
    (
        SELECT
            (
                TIME '00:00'
                + (interval_number * INTERVAL '10 minutes')
            )::TIME AS start_time
    ) AS starts

ORDER BY
    start_time,
    duration_hours;