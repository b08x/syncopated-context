# frozen_string_literal: true

module AppName
  class App
    # ── Model ─────────────────────────────────────────────────────────────
    State = Struct.new(
      :active_screen,
      :status_message,
      :loading,
      keyword_init: true
    )

    def initialize
      @state = State.new(
        active_screen: :main,
        status_message: nil,
        loading: false
      )
    end

    # ── Update ────────────────────────────────────────────────────────────
    def update(message)
      case message
      in :quit
        [self, Bubbletea.quit]
      in { switch_screen: Symbol => screen }
        @state = @state.with(active_screen: screen)
      in { status: String => msg }
        @state = @state.with(status_message: msg)
      else
        active_screen&.update(message)
      end
    end

    # ── View ──────────────────────────────────────────────────────────────
    def view
      Lipgloss.join_vertical(
        :left,
        header_view,
        active_screen&.view || "",
        status_bar_view
      )
    end

    private

    def active_screen
      @screens ||= {
        main: Screens::Main.new,
        # TODO: add screens here
      }
      @screens[@state.active_screen]
    end

    def header_view
      Styles::HEADER.render(" #{APP_NAME} ")
    end

    def status_bar_view
      Styles::STATUS_BAR.render(@state.status_message || " Ready")
    end
  end
end
