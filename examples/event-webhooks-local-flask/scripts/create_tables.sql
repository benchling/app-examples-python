CREATE TABLE IF NOT EXISTS synced_benchling_data (
  synced_entity_id SERIAL PRIMARY KEY,
  entity_name VARCHAR(300) NOT NULL,
  benchling_api_id VARCHAR(30) NOT NULL,
  field_value VARCHAR(300),
  synced_datetime TIMESTAMPTZ DEFAULT NOW() NOT NULL
);