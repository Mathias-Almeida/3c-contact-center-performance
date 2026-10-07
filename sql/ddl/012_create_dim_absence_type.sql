CREATE TABLE dim_absence_type (
    absence_type_key SMALLSERIAL PRIMARY KEY,
    absence_type_code VARCHAR(20) NOT NULL UNIQUE,
    absence_type_name VARCHAR(100) NOT NULL,
    absence_category VARCHAR(50) NOT NULL,
    is_planned BOOLEAN NOT NULL DEFAULT FALSE,
    impacts_absenteeism BOOLEAN NOT NULL DEFAULT TRUE,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL,

    CONSTRAINT chk_absence_category
        CHECK (
            absence_category IN (
                'Absenteísmo',
                'Saúde',
                'Programada',
                'Afastamento',
                'Operacional',
                'Administrativa',
                'Jornada',
                'Disciplinar'
            )
        )
);