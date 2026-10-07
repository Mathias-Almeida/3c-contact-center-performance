INSERT INTO dim_absence_type (
    absence_type_code,
    absence_type_name,
    absence_category,
    is_planned,
    impacts_absenteeism,
    is_paid,
    is_active,
    created_date
)
VALUES
    (
        'ABS001',
        'Falta injustificada',
        'Absenteísmo',
        FALSE,
        TRUE,
        FALSE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS002',
        'Atestado médico',
        'Saúde',
        FALSE,
        TRUE,
        TRUE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS003',
        'Férias',
        'Programada',
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS004',
        'Licença',
        'Afastamento',
        FALSE,
        TRUE,
        FALSE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS005',
        'Folga',
        'Programada',
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS006',
        'Treinamento',
        'Operacional',
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS007',
        'Abono',
        'Administrativa',
        FALSE,
        TRUE,
        TRUE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS008',
        'Afastamento',
        'Afastamento',
        FALSE,
        TRUE,
        FALSE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS009',
        'Banco de horas',
        'Jornada',
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        DATE '2026-01-01'
    ),
    (
        'ABS010',
        'Suspensão',
        'Disciplinar',
        FALSE,
        TRUE,
        FALSE,
        TRUE,
        DATE '2026-01-01'
    );