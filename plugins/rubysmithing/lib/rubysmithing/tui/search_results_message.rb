# frozen_string_literal: true

require "bubbletea"

module Rubysmithing
  module TUI
    # Message returned after an async search operation completes.
    class SearchResultsMessage < Bubbletea::Message
      attr_reader :results, :error

      # @param results [Array<Rubysmithing::RAG::Clause>] the retrieved clauses.
      # @param error [String, nil] the error message if the search failed.
      def initialize(results: [], error: nil)
        super()
        @results = results
        @error = error
      end
    end
  end
end
