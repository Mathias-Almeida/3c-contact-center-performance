WITH distribuicao AS (
    SELECT
        s.supervisor_key,
        o.organization_key
    FROM dim_supervisor s
    JOIN dim_organization o
        ON o.organization_code = 'COO' ||
           LPAD(
               CEIL(s.supervisor_key / 11.0)::TEXT,
               3,
               '0'
           )
)
UPDATE dim_supervisor s
SET organization_key = d.organization_key
FROM distribuicao d
WHERE s.supervisor_key = d.supervisor_key;