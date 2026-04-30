# frozen_string_literal: true

module Rubysmithing
  module RAG
    class Document < Sequel::Model
      one_to_many :clauses
    end
  end
end
