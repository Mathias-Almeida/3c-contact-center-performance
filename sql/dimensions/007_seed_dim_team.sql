INSERT INTO dim_team (
    team_code,
    team_name,
    supervisor_key,
    is_active,
    created_date
)
SELECT
    'TEAM' || LPAD(supervisor_key::TEXT, 3, '0') AS team_code,
    'Equipe ' || supervisor_code AS team_name,
    supervisor_key,
    TRUE AS is_active,
    DATE '2026-01-01' AS created_date
FROM dim_supervisor
ORDER BY supervisor_key;