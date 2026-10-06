INSERT INTO dim_channel (
    channel_code,
    channel_name,
    channel_description,
    is_active,
    created_date
)
VALUES
(
    'CH001',
    'Voice',
    'Atendimento realizado por telefone',
    TRUE,
    '2026-01-01'
),
(
    'CH002',
    'Chat',
    'Atendimento realizado por chat digital',
    TRUE,
    '2026-01-01'
),
(
    'CH003',
    'WhatsApp',
    'Atendimento realizado pelo WhatsApp',
    TRUE,
    '2026-01-01'
),
(
    'CH004',
    'E-mail/Backoffice',
    'Tratamento de solicitações recebidas por e-mail e atividades de backoffice',
    TRUE,
    '2026-01-01'
);