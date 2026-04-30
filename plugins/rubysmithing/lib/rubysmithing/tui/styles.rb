# frozen_string_literal: true

require "lipgloss"

module Rubysmithing
  module TUI
    module Styles
      # Semantic Color System (Layer 1)
      COLORS = {
        fg_default:   "#D8DEE9",
        fg_muted:     "#7B8394",
        fg_emphasis:  "#FFFFFF",
        bg_base:      "#1A1B26",
        bg_surface:   "#24283B",
        accent:       "#7AA2F7",
        status_error: "#F7768E",
        mistral_teal: "#00A699"
      }.freeze

      # Style Constants (Layer 2)
      HEADER = Lipgloss::Style.new
        .bold(true)
        .foreground(COLORS[:fg_emphasis])
        .background(COLORS[:mistral_teal])
        .padding(0, 1)

      PANEL = Lipgloss::Style.new
        .border(:rounded)
        .border_foreground(COLORS[:fg_muted])
        .padding(0, 1)

      ACTIVE_PANEL = PANEL.copy
        .border_foreground(COLORS[:accent])

      TITLE = Lipgloss::Style.new
        .bold(true)
        .foreground(COLORS[:accent])

      METADATA = Lipgloss::Style.new
        .foreground(COLORS[:fg_muted])
        .italic(true)

      ERROR = Lipgloss::Style.new
        .foreground(COLORS[:status_error])
        .bold(true)

      # Legacy adapters (kept for internal use but preferring Components::Base)
      def self.render_header(text)
        HEADER.render(text.upcase)
      end

      def self.render_panel(text)
        PANEL.render(text)
      end
    end
  end
end
