# frozen_string_literal: true

module AppName
  module Components
    # Internal adapter — isolates Bubble gem API surface.
    # All screens and components call through this module.
    # If bubbletea/lipgloss APIs change, update here only.
    module Base
      def self.panel(content, style: AppName::Styles::PANEL)
        style.render(content)
      end

      def self.active_panel(content)
        AppName::Styles::ACTIVE_PANEL.render(content)
      end

      def self.join_vertical(*parts, align: :left)
        Lipgloss.join_vertical(align, *parts)
      end

      def self.join_horizontal(*parts, align: :top)
        Lipgloss.join_horizontal(align, *parts)
      end

      def self.render_markdown(text)
        # Verify Glamour API via rubysmithing-context before use
        Glamour.render(text)
      end

      # Focus state helpers — use in view methods to dim unfocused panels.
      # Focused panel:   Components::Base.active_panel(content)
      # Unfocused panel: Components::Base.focus_dim(content)
      FOCUS_DIM_STYLE = Lipgloss::Style.new
        .foreground(AppName::Styles::COLORS[:fg_muted])

      def self.focus_dim(content)
        FOCUS_DIM_STYLE.render(content)
      end

      def self.focus_bright(content)
        AppName::Styles::ACTIVE_PANEL.render(content)
      end
    end
  end
end
