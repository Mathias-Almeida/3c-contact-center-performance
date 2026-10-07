INSERT INTO dim_skill (
    skill_code,
    skill_name,
    operation_key,
    channel_key,
    skill_description,
    is_active,
    created_date
)
VALUES
(
    'V001',
    'SAC Voice',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP001'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH001'),
    'Atendimento de SAC pelo canal de voz',
    TRUE,
    '2026-01-01'
),
(
    'V002',
    'Financeiro Voice',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP002'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH001'),
    'Atendimento financeiro pelo canal de voz',
    TRUE,
    '2026-01-01'
),
(
    'V003',
    'Retenção Voice',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP003'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH001'),
    'Atendimento de retenção pelo canal de voz',
    TRUE,
    '2026-01-01'
),
(
    'V004',
    'Suporte Técnico Voice',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP004'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH001'),
    'Atendimento de suporte técnico pelo canal de voz',
    TRUE,
    '2026-01-01'
),
(
    'V005',
    'Vendas Voice',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP005'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH001'),
    'Atendimento comercial pelo canal de voz',
    TRUE,
    '2026-01-01'
),
(
    'C001',
    'SAC Chat',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP001'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH002'),
    'Atendimento de SAC pelo canal de chat',
    TRUE,
    '2026-01-01'
),
(
    'C002',
    'Suporte Chat',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP004'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH002'),
    'Atendimento de suporte técnico pelo canal de chat',
    TRUE,
    '2026-01-01'
),
(
    'C003',
    'Vendas Chat',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP005'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH002'),
    'Atendimento comercial pelo canal de chat',
    TRUE,
    '2026-01-01'
),
(
    'W001',
    'SAC WhatsApp',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP001'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH003'),
    'Atendimento de SAC pelo WhatsApp',
    TRUE,
    '2026-01-01'
),
(
    'W002',
    'Financeiro WhatsApp',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP002'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH003'),
    'Atendimento financeiro pelo WhatsApp',
    TRUE,
    '2026-01-01'
),
(
    'W003',
    'Suporte WhatsApp',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP004'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH003'),
    'Atendimento de suporte técnico pelo WhatsApp',
    TRUE,
    '2026-01-01'
),
(
    'E001',
    'E-mail/Backoffice',
    (SELECT operation_key FROM dim_operation WHERE operation_code = 'OP001'),
    (SELECT channel_key FROM dim_channel WHERE channel_code = 'CH004'),
    'Tratamento de solicitações de SAC por e-mail e atividades de backoffice',
    TRUE,
    '2026-01-01'
);