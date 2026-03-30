# frozen_string_literal: true

module AppName
  module Styles
    # ── Semantic Color Tokens ────────────────────────────────────────────
    # Edit this section to retheme the entire application.
    # All structural styles below consume tokens by key — never use raw
    # hex values in component or screen files.
    # NO_COLOR: when ENV["NO_COLOR"] is set, Lipgloss strips color
    # automatically. The TUI remains usable via bold/dim/underline alone.
    COLORS = {
      # Foreground
      fg_default: "#D8DEE9", # body text
      fg_muted: "#7B8394", # secondary text, metadata, timestamps
      fg_emphasis: "#FFFFFF", # headers, focused items, titles
      fg_on_accent: "#000000", # text on accent-colored background

      # Background
      bg_base: "#1A1B26", # primary app background (darkest)
      bg_surface: "#24283B",  # panel / widget backgrounds
      bg_overlay: "#2F3549",  # popup / dialog backgrounds
      bg_selection: "#364A82", # selected item highlight

      # Accent
      accent_primary: "#7AA2F7", # interactive elements, focus borders
      accent_secondary: "#BB9AF7", # supporting interactions, hints

      # Status — always pair with a symbol; never rely on color alone
      status_error: "#F7768E", # ✗ error
      status_warning: "#E0AF68",  # ⚠ warning
      status_success: "#9ECE6A",  # ✓ success
      status_info: "#7DCFFF", # ℹ info
    }.freeze

    # ── Structural Styles (consume tokens above) ─────────────────────────
    HEADER = Lipgloss::Style.new
      .bold(true)
      .foreground(COLORS[:fg_emphasis])
      .background(COLORS[:bg_overlay])
      .padding(0, 1)

    STATUS_BAR = Lipgloss::Style.new
      .foreground(COLORS[:fg_muted])
      .padding(0, 1)

    PANEL = Lipgloss::Style.new
      .border(:rounded)
      .border_foreground(COLORS[:fg_muted])
      .padding(0, 1)

    ACTIVE_PANEL = Lipgloss::Style.new
      .border(:rounded)
      .border_foreground(COLORS[:accent_primary])
      .padding(0, 1)

    SIDEBAR = Lipgloss::Style.new
      .width(30)
      .border(:rounded)
      .border_foreground(COLORS[:fg_muted])
      .padding(0, 1)

    # ── Status Indicator Styles ──────────────────────────────────────────
    STATUS_ERROR   = Lipgloss::Style.new.foreground(COLORS[:status_error])
    STATUS_WARNING = Lipgloss::Style.new.foreground(COLORS[:status_warning])
    STATUS_SUCCESS = Lipgloss::Style.new.foreground(COLORS[:status_success])
    STATUS_INFO    = Lipgloss::Style.new.foreground(COLORS[:status_info])
  end
end
