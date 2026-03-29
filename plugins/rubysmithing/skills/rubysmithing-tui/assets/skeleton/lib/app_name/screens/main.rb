# frozen_string_literal: true

module AppName
  module Screens
    class Main
      State = Struct.new(:cursor, :items, keyword_init: true)

      def initialize
        @state = State.new(cursor: 0, items: [])
      end

      def update(message)
        case message
        in :cursor_up
          @state = @state.with(cursor: [@state.cursor - 1, 0].max)
        in :cursor_down
          max = [@state.items.length - 1, 0].max
          @state = @state.with(cursor: [@state.cursor + 1, max].min)
        end
      end

      def view
        content = if @state.items.empty?
          "  (empty)"
        else
          @state.items.each_with_index.map do |item, i|
            (i == @state.cursor) ? "▶ #{item}" : "  #{item}"
          end.join("\n")
        end

        Styles::PANEL.render(content)
      end
    end
  end
end
