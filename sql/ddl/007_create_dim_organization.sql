CREATE TABLE dim_organization (
    organization_key SMALLSERIAL PRIMARY KEY,
    organization_code VARCHAR(20) NOT NULL UNIQUE,
    organization_name VARCHAR(100) NOT NULL,
    organization_level VARCHAR(30) NOT NULL,
    parent_organization_key SMALLINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_date DATE NOT NULL,

    CONSTRAINT fk_organization_parent
        FOREIGN KEY (parent_organization_key)
        REFERENCES dim_organization(organization_key)
);