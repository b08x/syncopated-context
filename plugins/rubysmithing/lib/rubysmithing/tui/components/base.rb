# frozen_string_literal: true

require "lipgloss"

module Rubysmithing
  module TUI
    module Components
      # The central adapter for all TUI rendering. 
      # Ensures that Lipgloss calls are never inlined in screens.
      module Base
        module_function

        def header(text)
          Styles::HEADER.render(text.upcase)
        end

        def panel(text, focused: false)
          style = focused ? Styles::ACTIVE_PANEL : Styles::PANEL
          style.render(text)
        end

        def error(text)
          Styles::ERROR.render("ERROR: #{text}")
        end

        def title(text)
          Styles::TITLE.render(text)
        end

        def metadata(text)
          Styles::METADATA.render(text)
        end

        def join_vertical(alignment, *components)
          Lipgloss.join_vertical(alignment, *components)
        end

        def join_horizontal(alignment, *components)
          Lipgloss.join_horizontal(alignment, *components)
        end
      end
    end
  end
end
