# frozen_string_literal: true

require "bubbletea"
require "bubbles"
require "lipgloss"

module Rubysmithing
  module TUI
    # The primary interface for RAG operations.
    # Handles query input and displays retrieved clauses using an async command pattern.
    class Dashboard
      include Bubbletea::Model

      # @param retriever [Rubysmithing::RAG::Retriever] the retrieval engine.
      def initialize(retriever)
        @retriever = retriever
        @query_input = Bubbles::TextInput.new
        @query_input.placeholder = "Enter query to retrieve clauses..."
        @query_input.focus

        @results = []
        @loading = false
        @error = nil
      end

      # Initializes the model.
      # @return [Array(Bubbles::TextInput, nil)]
      def init
        [@query_input, nil]
      end

      # Updates the model based on the received message.
      # @param message [Object] the incoming message (KeyMessage, SearchResultsMessage, etc.)
      # @return [Array(self, Proc, nil)] the updated model and an optional command.
      def update(message)
        case message
        when SearchResultsMessage
          return handle_results(message)
        when Bubbletea::KeyMessage
          return handle_key(message)
        end

        @query_input, cmd = @query_input.update(message)
        [self, cmd]
      end

      # Renders the current state of the dashboard.
      # @return [String] the formatted TUI view.
      def view
        header = Components::Base.header("Rubysmithing RAG Dashboard")
        input_view = Components::Base.panel("Query: #{@query_input.view}", focused: true)

        results_view = if @loading
                         "Searching..."
                       elsif @error
                         Components::Base.error(@error)
                       elsif @results.empty?
                         "No results yet. Enter a query above and press Enter."
                       else
                         render_results
                       end

        Components::Base.join_vertical(
          :left,
          header,
          "",
          input_view,
          "",
          "Results:",
          "",
          results_view
        )
      end

      private

      def handle_key(message)
        case message.to_s
        when "ctrl+c", "q"
          [self, Bubbletea.quit]
        when "enter"
          handle_search
        else
          [self, nil]
        end
      end

      def handle_results(message)
        @loading = false
        if message.error
          @error = message.error
          @results = []
        else
          @results = message.results
        end
        [self, nil]
      end

      def handle_search
        return [self, nil] if @query_input.value.strip.empty?

        @loading = true
        @error = nil
        query = @query_input.value

        # Sovereign Decision: Using a Proc as a command to offload retrieval to a background fiber.
        # This prevents blocking the UI thread during API calls.
        search_cmd = proc do
          begin
            results = @retriever.retrieve(query: query)
            SearchResultsMessage.new(results: results)
          rescue StandardError => e
            SearchResultsMessage.new(error: e.message)
          end
        end

        [self, search_cmd]
      end

      def render_results
        @results.map do |clause|
          doc_title = clause.document&.title || "Unknown Document"
          Components::Base.join_vertical(
            :left,
            Components::Base.title(doc_title),
            clause.content,
            Components::Base.metadata("Distance: #{clause.values[:distance].round(4)}")
          )
        end.join("\n\n")
      end
    end
  end
end
