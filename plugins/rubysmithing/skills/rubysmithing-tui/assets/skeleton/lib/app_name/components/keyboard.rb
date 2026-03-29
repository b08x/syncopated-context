# frozen_string_literal: true

module AppName
  module Components
    # Four-layer keyboard architecture.
    #
    # L0 Universal  — always active (arrows, Enter, Esc, q, Tab)
    # L1 Vim Motions — opt-in for navigation-heavy apps (hjkl)
    # L2 Actions    — domain mnemonics; populate per-app (see L2 hash below)
    # L3 Power      — command palette / macros; activate for 20+ action apps
    #
    # Usage in app's update method:
    #   when Bubbletea::KeyMessage
    #     if (action = Components::Keyboard.resolve(message.to_s, layers: [:l0, :l1]))
    #       dispatch_action(action, state)
    #
    # See references/design-patterns.md §3 for full architecture and key conventions.
    module Keyboard
      # L0: Universal — wire in every app
      L0 = {
        up: :cursor_up,
        down: :cursor_down,
        left: :focus_prev,
        right: :focus_next,
        enter: :confirm,
        escape: :cancel_or_back,
        tab: :focus_next_panel,
        shift_tab: :focus_prev_panel,
        q: :quit,
      }.freeze

      # L1: Vim motions — include when domain is navigation-heavy
      # Note: "h" (collapse/back) takes priority over any domain mnemonic
      L1 = {
        j: :cursor_down,
        k: :cursor_up,
        h: :collapse_or_back,
        l: :expand_or_forward,
        g: :goto_top,
        G: :goto_bottom,
      }.freeze

      # L2: Domain-specific action mnemonics — populate per-app.
      # Example: { "n": :new_item, "d": :delete, "e": :edit, "p": :preview }
      L2 = {}.freeze

      # Resolve a keypress through the specified active layers.
      # Returns the mapped action Symbol, or nil if no binding found.
      #
      # @param key [String, Symbol] the key received from BubbleTea
      # @param layers [Array<Symbol>] active layers in priority order
      # @return [Symbol, nil]
      def self.resolve(key, layers: [:l0])
        layer_map = { l0: L0, l1: L1, l2: L2 }
        layers.each do |layer|
          msg = layer_map[layer]&.fetch(key.to_sym, nil)
          return msg if msg
        end
        nil
      end
    end
  end
end
