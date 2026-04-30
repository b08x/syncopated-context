# frozen_string_literal: true

require "pragmatic_segmenter"
require "ruby_llm"
require "digest"

module Rubysmithing
  module RAG
    class Ingester
      def initialize(db)
        @db = db
      end

      def ingest(title:, text:, metadata: {})
        document = Document.create(title: title, metadata: metadata.to_json)
        
        segments = PragmaticSegmenter::Segmenter.new(text: text).segment
        
        @db.transaction do
          segments.each do |segment|
            embedding = generate_embedding(segment)
            Clause.create(
              document_id: document.id,
              content: segment,
              embedding: embedding
            )
          end
        end
        
        document
      end

      private

      def generate_embedding(text)
        # In a real app, we'd use RubyLLM.embed(text)
        # For this example, if no API key is set, we return a deterministic random vector
        if ENV["OPENAI_API_KEY"] || ENV["ANTHROPIC_API_KEY"]
          begin
            RubyLLM.embed(text).vector
          rescue StandardError
            fake_vector(text)
          end
        else
          fake_vector(text)
        end
      end

      def fake_vector(text)
        # Deterministic vector based on text hash
        hash = Digest::SHA256.digest(text).unpack("C*")
        # Normalize to 384 dimensions (padding/truncating)
        vector = (0...384).map { |i| (hash[i % hash.size] / 255.0).round(4) }
        vector
      end
    end
  end
end
