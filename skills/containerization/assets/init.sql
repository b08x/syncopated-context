-- PGVector initialization script
-- Mounted to /docker-entrypoint-initdb.d/ in the postgres container
-- Runs automatically on first database creation

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Example: embeddings table (customize per project)
-- CREATE TABLE IF NOT EXISTS embeddings (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     content TEXT NOT NULL,
--     embedding vector(1536),  -- Adjust dimension to model output
--     metadata JSONB DEFAULT '{}',
--     created_at TIMESTAMPTZ DEFAULT NOW()
-- );
-- CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON embeddings
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
