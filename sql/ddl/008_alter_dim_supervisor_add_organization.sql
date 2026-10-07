ALTER TABLE dim_supervisor
ADD COLUMN organization_key SMALLINT;

ALTER TABLE dim_supervisor
ADD CONSTRAINT fk_supervisor_organization
FOREIGN KEY (organization_key)
REFERENCES dim_organization(organization_key);