# TUI Patterns (Context7-Verified)

Component patterns for the Ruby Charm/Bubble ecosystem. All patterns verified against Context7.
Always run `rubysmithing-context` before generating if the gem API is not covered here.

## Contents
- [Verified Context7 Library IDs](#verified-context7-library-ids)
- [Bubbletea Model Interface](#bubbletea-model-interface-verified)
- [Lipgloss Styles](#lipgloss-styles-verified)
- [Styles Module](#styles-module-verified)
- [Two-Pane Layout](#two-pane-layout-verified)
- [Bubbles::TextInput](#bubblestextinput-verified)
- [Bubbles::List](#bubbleslist-verified)
- [Bubbles::Spinner](#bubblesspinner-verified)
- [Bubbles::Cursor](#bubblescursor-verified)
- [Bubbles::Help](#bubbleshelp-verified)
- [Huh Forms](#huh-forms-verified)
- [Gum Prompts](#gum-prompts-verified)

**Verified source of truth:** `docker/prompt.txt` — if this file conflicts with `docker/prompt.txt`,
the prompt file takes precedence.

### Migration Guide (Legacy → Verified API)

| Legacy (Do Not Use) | Verified API | Notes |
|:---|:---|:---|
| `BubbleTea::Quit` | `Bubbletea.quit` | Module method, lowercase |
| `Lipgloss::Align::LEFT` | `:left` | Symbol, no class wrapper |
| `Lipgloss::Color.new("#HEX")` | `.foreground("#HEX")` | Plain hex string |
| `Struct.new(...).with(...)` for App state | plain `@ivar` | App-level state only |

---

## Verified Context7 Library IDs

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

---

## Bubbletea Model Interface (Verified)

Every app MUST implement the `Bubbletea::Model` interface:

```ruby
# Entry point
Bubbletea.run(App.new)

# Required mixin + methods
class App
  include Bubbletea::Model

  def initialize
    @state = "initial"  # plain @ivar — NOT Struct.with
  end

  def init
    [self, nil]  # [model, command] — nil = no startup command
  end

  def update(message)
    case message
    when Bubbletea::WindowSizeMessage
      @width = message.width
      @height = message.height
      [self, nil]

    when Bubbletea::KeyMessage
      case message.to_s
      when "q", "ctrl+c"
        [self, Bubbletea.quit]  # ← VERIFIED: Bubbletea.quit (not BubbleTea::Quit)
      when "up", "k"
        @count += 1
        [self, nil]
      when "down", "j"
        @count -= 1
        [self, nil]
      else
        [self, nil]
      end

    else
      [self, nil]
    end
  end

  def view
    "Count: #{@count}\nPress up/k to increment, down/j to decrement, q to quit"
  end
end
```

**Critical invariants (verified):**
- `update` ALWAYS returns `[self, command]` — never `nil` or bare model
- `Bubbletea.quit` (lowercase, module method) — NOT `BubbleTea::Quit`
- State in plain `@ivar` — NOT `Struct.new(...).with(...)` for App models
- `message.to_s` returns key strings: `"up"`, `"down"`, `"j"`, `"k"`, `"q"`, `"ctrl+c"`, etc.
- `Bubbletea::KeyMessage` helper methods: `.enter?`, `.esc?`, `.up?`, `.down?`, `.ctrl?`, `.char`

---

## Lipgloss Styles (Verified)

### Colors — plain hex strings, NO Color.new wrapper

```ruby
# VERIFIED: .foreground("#HEX") and .background("#HEX") — no Lipgloss::Color.new
style = Lipgloss::Style.new
  .bold(true)
  .foreground("#FAFAFA")
  .background("#7D56F4")
  .padding(1, 2)

# Adaptive colors (auto-switch dark/light terminal)
adaptive = Lipgloss::AdaptiveColor.new(light: "#000000", dark: "#FFFFFF")

# Complete colors with fallbacks
complete = Lipgloss::CompleteColor.new(
  true_color: "#FF6B6B",
  ansi256: 196,
  ansi: :bright_red
)
```

### Alignment — symbols only, NO Lipgloss::Align namespace

```ruby
# VERIFIED: :left, :top, :center, :right — NOT Lipgloss::Align::LEFT
Lipgloss::Style.new
  .width(40)
  .align_horizontal(:center)
  .align_vertical(:top)

# Combined alignment
Lipgloss::Style.new
  .width(40).height(5)
  .align(:center, :center)  # horizontal, vertical
  .border(:rounded)
```

### Layout joins — alignment as first positional arg

```ruby
# VERIFIED: alignment symbol as first argument
Lipgloss.join_horizontal(:top, left, middle, right)
Lipgloss.join_vertical(:left, header, body, footer)

# With explicit positioning
Lipgloss.place(60, 10, :center, :center, "Content")
Lipgloss.place_horizontal(40, :center, "Centered in 40 cols")
Lipgloss.place_vertical(5, :center, "Centered in 5 rows")
```

---

## Styles Module (Verified)

```ruby
# lib/[app_name]/styles.rb
# frozen_string_literal: true

module AppName
  module Styles
    # Token layer — all colors as plain hex strings
    COLORS = {
      fg_default:   "#D8DEE9",
      fg_muted:     "#7B8394",
      fg_emphasis:  "#FFFFFF",
      bg_base:      "#1A1B26",
      bg_surface:   "#24283B",
      accent:       "#7AA2F7",
      status_error: "#F7768E"
    }.freeze

    # Style constants consume tokens (plain hex — no Color.new)
    HEADER = Lipgloss::Style.new
      .bold(true)
      .foreground(COLORS[:fg_emphasis])
      .background(COLORS[:accent])
      .padding(0, 1)

    PANEL = Lipgloss::Style.new
      .border(:rounded)
      .border_foreground(COLORS[:fg_muted])
      .padding(0, 1)

    ACTIVE_PANEL = PANEL.copy
      .border_foreground(COLORS[:accent])

    SIDEBAR = Lipgloss::Style.new
      .width(30)
      .border(:rounded)
      .padding(0, 1)

    MAIN_PANE = Lipgloss::Style.new
      .border(:rounded)
      .padding(0, 1)
  end
end
```

---

## Two-Pane Layout (Verified)

```ruby
def view
  sidebar = Styles::SIDEBAR.render(sidebar_content)
  main    = Styles::MAIN_PANE.render(main_content)

  # VERIFIED: alignment as first positional arg, plain symbol
  Lipgloss.join_horizontal(:top, sidebar, main)
end
```

---

## Bubbles::TextInput (Verified)

```ruby
# Query: /marcoroth/bubbles-ruby "TextInput placeholder focus update view value"

input = Bubbles::TextInput.new
input.placeholder = "Enter your username..."
input.prompt = "> "
input.char_limit = 20
input.width = 30
input.focus

# Optional: Password mode
input.echo_mode = :password
input.echo_character = "*"

# Optional: Suggestions
input.suggestions = ["admin", "user", "guest"]
input.show_suggestions = true

# Optional: Validation
input.validate = ->(value) {
  return StandardError.new("Too short") if value.length < 3
  nil
}

# In update — returns [input, command]
input, command = input.update(message)

# In view
input.view

# Get value
input.value
```

**Key bindings for TextInput:**
- Left/Right, Ctrl+B/F — Move cursor
- Home/End, Ctrl+A/E — Jump to start/end
- Backspace, Delete — Delete characters
- Ctrl+K/U — Delete to end/start of line
- Ctrl+W, Alt+Backspace — Delete word backward
- Tab — Accept suggestion
- Up/Down — Cycle through suggestions

---

## Bubbles::List (Verified)

```ruby
# Query: /marcoroth/bubbles-ruby "List items selection navigation update view"

list = Bubbles::List.new(items, width: 50, height: 12)
list.title = "Items"

# In update — returns [list, command]
list, command = list.update(message)

# In view
list.view

# Navigation helpers
list.selected_index
list.items = new_items
```

---

## Bubbles::Spinner (Verified)

```ruby
# Query: /marcoroth/bubbles-ruby "Spinner animation tick stop"

spinner = Bubbles::Spinner.new(spinner: Bubbles::Spinners::DOT)

# Start animation
command = spinner.tick

# Update (returns [spinner, command])
spinner, command = spinner.update(message)

# Stop
spinner.stop

# Available styles:
# Bubbles::Spinners::LINE, DOT, MINI_DOT, JUMP, PULSE, POINTS,
# GLOBE, MOON, MONKEY, METER, HAMBURGER, ELLIPSIS
```

---

## Bubbles::Cursor (Verified)

```ruby
# Query: /marcoroth/bubbles-ruby "Cursor blink mode char"

cursor = Bubbles::Cursor.new
cursor.char = "_"
cursor.blink_speed = 0.53

# Focus to start
command = cursor.focus
cursor.blur  # Disable

# Set mode
cursor.set_mode(:blink)    # Bubbles::Cursor::MODE_BLINK
cursor.set_mode(:static)    # Bubbles::Cursor::MODE_STATIC
cursor.set_mode(:hide)      # Bubbles::Cursor::MODE_HIDE

# Update (returns [cursor, command])
cursor, command = cursor.update(message)

cursor.view
cursor.focused?
cursor.blink?
```

---

## Bubbles::Help (Verified)

```ruby
# Query: /marcoroth/bubbles-ruby "Help key binding short_help_view full_help_view"

KEYS = {
  up:    Bubbles::Key.binding(keys: ["up", "k"], help: ["↑/k", "up"]),
  down:  Bubbles::Key.binding(keys: ["down", "j"], help: ["↓/j", "down"]),
  quit:  Bubbles::Key.binding(keys: ["q"], help: ["q", "quit"]),
  help:  Bubbles::Key.binding(keys: ["?"], help: ["?", "help"])
}

# In view
help = Bubbles::Help.new
help.short_help_view([KEYS[:help], KEYS[:quit]])
# Renders: "? help • q quit"

help.full_help_view([
  [KEYS[:up], KEYS[:down]],
  [KEYS[:help], KEYS[:quit]]
])
# Renders in columns

# Check match
if Bubbles::Key.matches?(message, KEYS[:quit])
  # Handle quit
end
```

---

## Huh Forms (Verified)

### Functional DSL

```ruby
# Query: /marcoroth/huh-ruby "form group input select confirm validation theme"

form = Huh.form(
  Huh.group(
    Huh.input
      .key("name")
      .title("What's your name?")
      .placeholder("Enter your name..."),

    Huh.input
      .key("email")
      .title("Email address")
      .placeholder("you@example.com")
      .validate(Huh::Validation.not_empty)
      .validate(Huh::Validation.email),

    Huh.select
      .key("role")
      .title("Account type")
      .options("Personal", "Business", "Enterprise")
      .filtering(true),

    Huh.confirm
      .key("newsletter")
      .title("Subscribe to newsletter?")
      .affirmative("Yes!")
      .negative("No thanks")

  ).title("User Registration")
).with_theme(Huh::Themes.charm)

# Run
errors = form.run

if errors.any?
  puts "Errors: #{errors.map(&:message).join(', ')}"
else
  form.get("name")       # or form["name"]
  form.get("email")
  form.to_h             # => {"name" => "...", "email" => "...", ...}
end
```

### Block DSL

```ruby
# Query: /marcoroth/huh-ruby "Form.new block group input select"

form = Huh::Form.new do |f|
  f.theme(Huh::Themes.charm)

  f.group do |g|
    g.title("Server Configuration")

    g.input do |i|
      i.key("host")
      i.title("Hostname")
      i.placeholder("localhost")
      i.validate(Huh::Validation.not_empty)
    end

    g.input do |i|
      i.key("port")
      i.title("Port")
      i.validate(Huh::Validation.all(
        Huh::Validation.not_empty,
        Huh::Validation.integer,
        Huh::Validation.range(1, 65535)
      ))
    end

    g.select do |s|
      s.key("protocol")
      s.title("Protocol")
      s.options("HTTP", "HTTPS")
    end
  end
end

form.run
```

### Validators

```ruby
Huh::Validation.not_empty
Huh::Validation.email
Huh::Validation.integer
Huh::Validation.min_length(n)
Huh::Validation.max_length(n)
Huh::Validation.length(min, max)
Huh::Validation.range(min, max)
Huh::Validation.one_of("small", "medium", "large")
Huh::Validation.all(validator1, validator2, ...)

# Custom
input.validate do |value|
  raise Huh::ValidationError, "must start with @" unless value.start_with?("@")
end
```

---

## Gum Prompts (Verified)

```ruby
# Query: /marcoroth/gum-ruby "input choose filter"

# Single selection
color = Gum.choose(["red", "green", "blue"])
framework = Gum.choose("Rails", "Sinatra", "Hanami")

# Multiple selection with limit
colors = Gum.choose(%w[red green blue yellow], limit: 2)

# Unlimited multiple selection
selected = Gum.choose(items, no_limit: true, header: "Select:")

# With pre-selection
choice = Gum.choose(options, selected: ["option2"])

# Styling
choice = Gum.choose(options,
  header: "Pick one:",
  height: 10,
  cursor: ">",
  cursor_style: { foreground: "212" },
  selected_style: { foreground: "86", bold: true }
)

# Filter/search
file = Gum.filter(Dir.glob("**/*.rb"))
files = Gum.filter(items, placeholder: "Search...", height: 20)

# Text input
name = Gum.input(placeholder: "Enter your name")
password = Gum.input(password: true, placeholder: "Password")

# Styled input
username = Gum.input(
  header: "Create Account",
  placeholder: "username",
  width: 40,
  cursor: { foreground: "#FF0" }
)
```

---

## NTCharts (Verified)

### LineChart

```ruby
# Query: /marcoroth/ntcharts-ruby "Linechart draw_rune draw_braille_line draw_axes view"

chart = Ntcharts::Linechart.new(50, 12, 0.0, 10.0, 0.0, 10.0)

# Plot points with runes
(0..10).each do |i|
  x = i.to_f
  y = Math.sin(i * 0.5) * 4 + 5
  chart.draw_rune(x, y, "*")
end

# Or draw lines
chart.draw_line(0.0, 2.0, 10.0, 8.0, Ntcharts::Linechart::LINE_STYLE_THIN)
chart.draw_line(0.0, 2.0, 10.0, 8.0, Ntcharts::Linechart::LINE_STYLE_ARC)

chart.draw_axes
puts chart.view
```

### BarChart

```ruby
# Query: /marcoroth/ntcharts-ruby "Barchart push label values render"

chart = Ntcharts::Barchart.new(50, 12)

red_style = Ntcharts::Style.new.foreground("9")
green_style = Ntcharts::Style.new.foreground("2")

chart.push(
  label: "Sales",
  values: [
    { name: "Q1", value: 30, style: red_style },
    { name: "Q2", value: 45, style: green_style }
  ]
)

puts chart.render
```

---

## Glamour Markdown (Verified)

```ruby
# Query: /marcoroth/glamour-ruby "render markdown style theme width"

# Basic rendering
puts Glamour.render("# Hello **World**")

# Built-in styles
Glamour.render("# Hello", style: "dark")
Glamour.render("# Hello", style: "light")
Glamour.render("# Hello", style: "dracula")
Glamour.render("# Hello", style: "notty")  # No colors for non-TTY

# With options
Glamour.render(markdown, width: 80, emoji: true)

# Custom style hash
custom_style = {
  h1: { prefix: ">> ", color: "99", bold: true },
  strong: { bold: true, color: "196" },
  emph: { italic: true, color: "226" },
  code: { color: "203", background_color: "236" }
}
Glamour.render_with_style(markdown, custom_style)
```

---

## Harmonica Spring Animations (Verified)

```ruby
# Query: /marcoroth/harmonica-ruby "Spring fps delta_time angular_frequency damping_ratio"

# Create spring (damping_ratio: <1 = bouncy, 1 = critically damped, >1 = over-damped)
spring = Harmonica::Spring.new(
  delta_time: Harmonica.fps(60),
  angular_frequency: 6.0,
  damping_ratio: 0.5  # bouncy
)

# Animate
position = 0.0
velocity = 0.0
target = 100.0

loop do
  position, velocity = spring.update(position, velocity, target)
  # Render...

  break if (position - target).abs < 0.01
end

# Presets
# Bouncy: damping_ratio 0.3
# Smooth: damping_ratio 0.5
# Critically damped: damping_ratio 1.0
# Over-damped: damping_ratio 1.2
```

---

## BubbleZone Mouse Zones (Verified)

```ruby
# Query: /marcoroth/bubblezone-ruby "mark scan get in_bounds Bubblezone.new_global"

# Initialize global zone manager
Bubblezone.new_global

# Mark clickable zones
layout = Bubblezone.mark("submit_btn", "Submit")
items = ["Option A", "Option B", "Option C"].map.with_index do |item, i|
  Bubblezone.mark("item_#{i}", item)
end.join("\n")

# Scan and detect clicks
Bubblezone.scan(layout)

zone = Bubblezone.get("submit_btn")
if zone&.in_bounds?(message.x, message.y)
  # Handle click
end

# Iterate all zones at point
Bubblezone.each_in_bounds(x, y) do |id, zone|
  puts "Hit: #{id}"
end
```

### Bubbletea Integration

```ruby
# Handle mouse messages
when Bubbletea::MouseMessage
  if message.release? && (message.left? || message.button == 0)
    result = Bubblezone.find_in_bounds(message.x, message.y)
    if result
      id, _zone = result
      # Handle zone id
    end
  end
```

---

## Complete App Example (Verified)

```ruby
# lib/[app_name]/app.rb
# frozen_string_literal: true

module AppName
  class App
    include Bubbletea::Model

    KEYS = {
      up:   Bubbles::Key.binding(keys: ["up", "k"], help: ["↑/k", "up"]),
      down: Bubbles::Key.binding(keys: ["down", "j"], help: ["↓/j", "down"]),
      quit: Bubbles::Key.binding(keys: ["q"], help: ["q", "quit"]),
    }

    def initialize
      @count = 0
      @show_help = false
    end

    def init
      [self, nil]
    end

    def update(message)
      case message
      when Bubbletea::KeyMessage
        if Bubbles::Key.matches?(message, KEYS[:quit])
          return [self, Bubbletea.quit]
        elsif message.to_s == "?"
          @show_help = !@show_help
        elsif Bubbles::Key.matches?(message, KEYS[:up])
          @count += 1
        elsif Bubbles::Key.matches?(message, KEYS[:down])
          @count -= 1
        end
      end

      [self, nil]
    end

    def view
      help = Bubbles::Help.new
      help_view = if @show_help
        help.full_help_view([[KEYS[:up], KEYS[:down]], [KEYS[:quit]]])
      else
        help.short_help_view([KEYS[:quit]])
      end

      Lipgloss.join_vertical(:left,
        "Count: #{@count}",
        help_view
      )
    end
  end
end
```
