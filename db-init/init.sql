CREATE TABLE IF NOT EXISTS "3rd_lev_domains" (
  id SERIAL PRIMARY KEY,
  predeterminado VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_id ON "3rd_lev_domains" (id);

COPY "3rd_lev_domains"(predeterminado)
FROM '/docker-entrypoint-initdb.d/3rd_lev_domains.csv' 
DELIMITER '|' 
CSV HEADER;