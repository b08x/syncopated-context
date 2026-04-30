# frozen_string_literal: true

require "sequel"
require "pgvector"

module Rubysmithing
  module Database
    def self.connect
      db_url = ENV.fetch("DATABASE_URL", "postgres:///rubysmithing_rag")
      db = Sequel.connect(db_url)
      
      # Load extensions
      db.run("CREATE EXTENSION IF NOT EXISTS vector")
      db.run("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
      db.run("CREATE EXTENSION IF NOT EXISTS pg_trgm")
      
      db
    end

    def self.migrate(db)
      db.create_table?(:documents) do
        uuid :id, primary_key: true, default: Sequel.function(:uuid_generate_v4)
        String :title, text: true, null: false
        column :metadata, :jsonb, default: "{}"
        DateTime :created_at, default: Sequel::CURRENT_TIMESTAMP
      end

      db.create_table?(:clauses) do
        uuid :id, primary_key: true, default: Sequel.function(:uuid_generate_v4)
        foreign_key :document_id, :documents, type: :uuid, on_delete: :cascade
        Text :content, null: false
        column :embedding, "vector(384)" # Default to all-MiniLM-L6-v2 size
        DateTime :created_at, default: Sequel::CURRENT_TIMESTAMP
        
        index :embedding, type: "hnsw", op_class: "vector_cosine_ops"
      end
    end
  end
end
