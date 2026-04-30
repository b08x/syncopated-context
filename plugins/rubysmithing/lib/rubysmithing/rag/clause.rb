# frozen_string_literal: true

require "pgvector"

module Rubysmithing
  module RAG
    class Clause < Sequel::Model
      plugin :pgvector, :embedding
      
      many_to_one :document
    end
  end
end
