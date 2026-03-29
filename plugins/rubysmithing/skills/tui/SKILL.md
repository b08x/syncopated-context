---
name: tui
description: Terminal UI scaffolder and advisor for Ruby projects using the Charm/Bubble ecosystem. Activates on any mention of: TUI, terminal UI, terminal interface, terminal app, BubbleTea, bubbletea, Lipgloss, lipgloss, Bubbles, bubbles (UI components), Huh, huh form, form validation, Gum, gum prompts, NTCharts, charts, data visualization, Bubblezone, Glamour, glamour rendering, markdown display, Harmonica, harmonica animations, spring physics, smooth transitions, animated scrolling, file browser, file picker, directory browser, interactive terminal, multi-panel, split pane, sidebar, dashboard, control panel, monitor, keyboard navigation, cursor movement, human in the loop component, HIL interface, RAG viewer, agent control panel, streaming output panel, text input, spinner, list selection, metrics display, animated transitions, or progress bar within a terminal context. Always runs rubysmithing-context as prerequisite for Bubble gem API verification. Always produces full skeleton: app.rb + screens/ + components/ stubs. Specs only on explicit request.
---

# Rubysmithing — TUI

Scaffolder and advisor for terminal UI applications using the Ruby Charm/Bubble ecosystem.
Always produces a full skeleton. Generates against verified API syntax only.

## Step 1: Prerequisites (Always Run First)

Before generating any scaffold or component code:

1. **Activate rubysmithing-context** for each Bubble gem involved:
   bubbletea, lipgloss, bubbles (UI components), huh (forms), glamour (markdown), ntcharts (visualization), harmonica (animations), and any of: gum, bubblezone.
   Generate no component code until API syntax is confirmed or WARNING block is injected.

2. **Extract domain** from the request — what does this TUI control or display?

3. **Identify screens** — what distinct views does the user need?

4. **Identify components per screen** — lists, forms, text areas, charts, panels.

5. **Identify external data flows** — what systems does this TUI interact with?
   If AI/LLM systems are involved, note the genai dependency.

## Step 1b: Select Layout Paradigm

After domain analysis, select the structural layout before generating any skeleton code.
Load `$CLAUDE_PLUGIN_ROOT/references/design-patterns.md` Section 1 for anatomy diagrams and responsive strategies.

| Domain Signal | Paradigm | Skeleton Shape |
|:---|:---|:---|
| File browser / explorer | Miller Columns | Three panes: nav / content / preview |
| Git, CI/CD, DevOps | Persistent Multi-Panel | Fixed sidebar + main + log strip |
| System / process monitor | Widget Dashboard | Grid of independent metric panels |
| Data browser / catalog | Drill-Down Stack | Push/pop screen stack, Esc ascends |
| SQL, HTTP, IDE workflow | IDE Three-Panel | File tree / editor / output bottom |
| Shell augmentation | Overlay / Popup | Base view + modal layer on demand |
| Log viewer / event stream | Header + Scrollable List | Fixed header + virtual scroll body |

If no clear signal → default to two-pane (sidebar + main, from tui-patterns.md §Two-Pane Layout).

**Compound prompts** (e.g., "refactor this RAG pipeline AND build a TUI for it"):
Handle the TUI component here. State explicitly:
"Handling the TUI dashboard component. The RAG pipeline component should be
addressed with genai."

## Step 2: Detect Mode

**Scaffolding** — triggered by: create, build, scaffold, generate, write a TUI for.
Output: full skeleton (see structure below) + complete file content.

**Advisory** — triggered by: how do I, which component, explain, what's the best way.
Output: recommendation + minimal snippet. No full scaffold unless asked.

## Skeleton Structure (always output this shape)

```
[app_name]/
├── app.rb                               # Zeitwerk boot + Bubbletea.run
├── Gemfile
└── lib/
    └── [app_name]/
        ├── app.rb                       # Root App model (Model / Update / View)
        ├── styles.rb                    # Semantic color tokens + Lipgloss constants
        ├── screens/
        │   └── main.rb                  # Starter main screen
        └── components/
            ├── base.rb                  # Adapter: all Bubble API calls go here
            ├── keyboard.rb              # L0–L3 keyboard layer routing
            └── .keep                    # Stub; domain components added here
```

Copy the base skeleton from `$CLAUDE_PLUGIN_ROOT/assets/skeleton/` and rename `app_name` → the
actual application name (snake_case for files, CamelCase for module).

## Internal Component DSL

To protect against Bubble ecosystem API churn, generate TUI component code
through a stable internal adapter pattern rather than calling Bubble gem APIs directly
in every file. Define a thin `Components::Base` adapter in each scaffold:

```ruby
# lib/[app_name]/components/base.rb
# frozen_string_literal: true

module AppName
  module Components
    # Internal adapter — isolates Bubble gem API surface.
    # If bubbletea/lipgloss/bubbles APIs change, update here only.
    module Base
      # Layout helpers
      def self.panel(content, style: Styles::PANEL)
        style.render(content)
      end

      def self.join_vertical(*parts, align: :left)
        Lipgloss.join_vertical(align, *parts)
      end

      def self.join_horizontal(*parts, align: :top)
        Lipgloss.join_horizontal(align, *parts)
      end

      # Bubbles component wrappers
      def self.text_input(**options)
        input = Bubbles::TextInput.new
        options.each { |key, value| input.public_send("#{key}=", value) }
        input
      end

      def self.list(items, **options)
        list = Bubbles::List.new(items)
        options.each { |key, value| list.public_send("#{key}=", value) }
        list
      end

      def self.spinner(style: Bubbles::Spinners::DOT)
        Bubbles::Spinner.new(spinner: style)
      end

      # Gum utilities (for forms outside main TUI loop)
      def self.prompt_input(**options)
        Gum.input(**options)
      end

      def self.prompt_choose(items, **options)
        Gum.choose(items, **options)
      end

      def self.prompt_filter(items, **options)
        Gum.filter(items, **options)
      end

      # Huh form components (for complex forms)
      def self.form_input(key:, title:, **options)
        Huh.input.key(key).title(title).tap do |input|
          options.each { |k, v| input.public_send(k, v) }
        end
      end

      def self.form_select(key:, title:, options:, **config)
        Huh.select.key(key).title(title).options(*options).tap do |select|
          config.each { |k, v| select.public_send(k, v) }
        end
      end

      def self.form_confirm(key:, title:, **options)
        Huh.confirm.key(key).title(title).tap do |confirm|
          options.each { |k, v| confirm.public_send(k, v) }
        end
      end

      # Glamour markdown rendering
      def self.render_markdown(content, **options)
        Glamour.render(content, **options)
      end

      def self.markdown_renderer(**options)
        Glamour::Renderer.new(**options)
      end

      # NTCharts data visualization
      def self.line_chart(width, height, min_x, max_x, min_y, max_y)
        Ntcharts::Linechart.new(width, height, min_x, max_x, min_y, max_y)
      end

      def self.time_series_chart(width, height)
        Ntcharts::Timeserieslinechart.new(width, height)
      end

      def self.bar_chart(width, height)
        Ntcharts::Barchart.new(width, height)
      end

      # Harmonica spring animations
      def self.spring_animation(fps: 60, frequency: 6.0, damping: 0.5)
        Harmonica::Spring.new(
          delta_time: Harmonica.fps(fps),
          angular_frequency: frequency,
          damping_ratio: damping
        )
      end

      def self.smooth_spring(fps: 60)
        spring_animation(fps: fps, frequency: 5.0, damping: 1.0)  # Critically damped
      end

      def self.bouncy_spring(fps: 60)
        spring_animation(fps: fps, frequency: 6.0, damping: 0.3)  # Bouncy
      end
    end
  end
end
```

All screens and components call `Components::Base.panel(...)` and
`Components::Base.join_vertical(...)` rather than `Styles::X.render(...)` or
`Lipgloss.join_*` directly. If the Lipgloss API changes, only `components/base.rb`
needs updating.

## BubbleTea Conventions

- State in plain `@ivar` — NOT `Struct.with` for App models (Bubbletea passes `self`; Struct copies break reference)
- Update returns `[self, command]` — ALWAYS (never `nil` or bare model)
- `Bubbletea.quit` (module method) — NOT `BubbleTea::Quit`
- `message.to_s` returns key strings: `"up"`, `"down"`, `"j"`, `"k"`, `"q"`, `"ctrl+c"`
- View is pure function: no I/O, no side effects
- Styles as module-level constants in `styles.rb` — never inline in `view`
- All Lipgloss/Bubbles calls through `Components::Base` adapter — never inline

## Design System Reference

Load `$CLAUDE_PLUGIN_ROOT/references/design-patterns.md` for architectural decisions:

- **Section 1** — Layout paradigm anatomy + responsive collapse strategies
- **Section 2** — Semantic color tokens, `COLORS` hash mapping, NO_COLOR degradation
- **Section 3** — Four-layer keyboard architecture (L0 Universal → L3 Power)
- **Section 4** — Three-tier help system (footer always-on / `?` overlay / docs)
- **Section 5** — Focus management: Tab order, panel dimming, modal focus traps
- **Section 6** — Command Palette pattern for apps with 20+ actions
- **Section 7** — Anti-pattern checklist (ranked by frequency)
- **Section 8** — Compatibility checklist (size, color, terminal, keyboard, Elm purity)

## Patterns Reference

Load `$CLAUDE_PLUGIN_ROOT/references/tui-patterns.md` for verified component code examples. All patterns are
Context7-verified. If patterns here contradict `docker/prompt.txt`, use the prompt file
as source of truth.

Verified Context7 IDs (pre-mapped — no resolution calls needed):

| Gem | Context7 ID |
|:---|:---|
| bubbletea | `/marcoroth/bubbletea-ruby` |
| lipgloss | `/marcoroth/lipgloss-ruby` |
| bubbles | `/marcoroth/bubbles-ruby` |
| huh | `/marcoroth/huh-ruby` |
| gum | `/marcoroth/gum-ruby` |
| ntcharts | `/marcoroth/ntcharts-ruby` |
| glamour | `/marcoroth/glamour-ruby` |
| harmonica | `/marcoroth/harmonica-ruby` |
| bubblezone | `/marcoroth/bubblezone-ruby` |

Key verified patterns:

- **Entry:** `Bubbletea.run(App.new)` — NOT `BubbleTea::Program.new`
- **Quit:** `Bubbletea.quit` — NOT `BubbleTea::Quit`
- **Colors:** `.foreground("#HEX")` — NO `Lipgloss::Color.new` wrapper
- **Alignment:** `:left`, `:top` symbols — NOT `Lipgloss::Align::LEFT`
- **State:** plain `@ivar` for App models — NOT `Struct.with`

## Domain → Component Mapping

| Domain | Layout Paradigm | Screens | Key Components |
| :---- | :---- | :---- | :---- |
| File browser (GDrive etc.) | Miller Columns | Browser, Editor, Export | AnimatedFileList (Bubbles::List + Harmonica), PreviewPane (Glamour), StatusBar, ActionMenu |
| RAG configurator | Drill-Down Stack | Config, Ingest, Query, HIL | ConfigForm (Huh::Form), ChunkingOptions, ResultsViewer (Glamour), HilReview |
| Agent control panel | Persistent Multi-Panel | Dashboard, ToolLog | AgentStatus, ToolCallLog, StreamingOutput (Glamour), Intervention (Gum prompts) |
| Monitoring / metrics | Widget Dashboard | Dashboard | MetricsChart (NTCharts), LogViewer (Glamour), StatusGrid, LoadingSpinner (Bubbles::Spinner) |
| Data entry forms | Overlay / Popup | Input, Validation, Review | ConfigForm (Huh::Form), FormFields, ValidationPanel |
| Search/Filter interfaces | Header + Scrollable List | Search, Results, Filter | SearchInput (Bubbles::TextInput), FilteredList (Bubbles::List + Harmonica), ResultsPane |
| Documentation viewer | IDE Three-Panel | Reader, Search, TOC | ContentViewer (Glamour), AnimatedNavigation (Bubbles::List + Harmonica), SearchBar |
| Analytics dashboard | Widget Dashboard | Overview, Charts, Reports | TimeSeriesChart (NTCharts), MetricsPanels, DataTable (Bubbles::List) |
| Interactive tutorials | Drill-Down Stack | Steps, Progress, Navigation | ProgressBar (Harmonica), StepNavigation, ContentDisplay (Glamour) |
| Live data feeds | Header + Scrollable List | Stream, Filters, Controls | SmoothScrolling (Harmonica), DataList (Bubbles::List), FilterControls |

## Output Format

For scaffolds:

1. **Full file tree** — every file to be created
2. **Complete content** for each file — screens/components left as minimal stubs only if
   they require domain-specific data flows not yet defined
3. **Gemfile additions** — all Bubble gems required
4. **Boot instruction** — `bundle exec ruby app.rb`
5. **Context7 IDs used** — or WARNING blocks if resolution failed

For advisory:

1. **Direct recommendation** with gem/component rationale
2. **Minimal snippet** for the specific pattern
3. **No full scaffold** unless asked

## Specs

Generate RSpec specs only when explicitly requested:

- Test Update function (pure, testable without rendering)
- Focus on state transitions, not view output
- File: `spec/[path]_spec.rb`
