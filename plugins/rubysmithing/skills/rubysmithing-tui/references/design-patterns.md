# TUI Design Patterns Reference

Architectural decisions for Ruby TUI applications. Covers layout selection,
color systems, keyboard architecture, help systems, and quality checklists.

For API syntax (component code examples), see `tui-patterns.md` — all patterns
are verified against Context7. The canonical verified source is `docker/prompt.txt`.

## Contents
- [1. Layout Paradigms](#1-layout-paradigms)
- [2. Semantic Color System](#2-semantic-color-system)
- [3. Keyboard Architecture](#3-keyboard-architecture)
- [4. Three-Tier Help System](#4-three-tier-help-system)
- [5. Focus Management](#5-focus-management)
- [6. Command Palette Pattern](#6-command-palette-pattern)
- [7. Anti-Pattern Checklist](#7-anti-pattern-checklist)
- [8. Compatibility Checklist](#8-compatibility-checklist)


> **Important:** `tui-patterns.md` is the verified reference. If you find patterns
> here that contradict it, use `docker/prompt.txt` as the source of truth.

---

## 1. Layout Paradigms

Select the paradigm before generating any skeleton. Domain signal determines structure.

| Domain Signal | Paradigm | Skeleton Shape |
|:---|:---|:---|
| File browser / explorer | Miller Columns | Three panes: nav / content / preview |
| Git, CI/CD, DevOps | Persistent Multi-Panel | Fixed sidebar + main + log strip |
| System / process monitor | Widget Dashboard | Grid of independent metric panels |
| Data browser / catalog | Drill-Down Stack | Push/pop screen stack, Esc ascends |
| SQL, HTTP, IDE workflow | IDE Three-Panel | File tree / editor / output bottom |
| Shell augmentation | Overlay / Popup | Base view + modal layer on demand |
| Log viewer / event stream | Header + Scrollable List | Fixed header + virtual scroll body |

If no clear signal → default to two-pane (existing sidebar + main recipe in tui-patterns.md §Two-Pane Layout).

### Paradigm Anatomy

**Miller Columns**
```
┌──────────┬───────────────────┬──────────────────┐
│ Nav      │ Content           │ Preview / Meta   │
│ ▶ dir/   │ file_a.rb         │ # frozen_string  │
│   dir2/  │ file_b.rb         │ module Foo       │
│   dir3/  │ ▶ file_c.rb       │   ...            │
└──────────┴───────────────────┴──────────────────┘
```
- Left: parent hierarchy navigation
- Center: current directory / list
- Right: preview adapts to selection type (code, image, config)
- `l` / Enter descends, `h` / Esc ascends

**Persistent Multi-Panel**
```
┌────────────┬──────────────────────────────────┐
│ Sidebar    │ Main Content                     │
│ ● branch   │                                  │
│   status   ├──────────────────────────────────┤
│   log      │ Log Strip                        │
└────────────┴──────────────────────────────────┘
```
- All panels visible simultaneously; Tab shifts focus
- Panels in fixed positions — users build spatial memory
- Log strip persists across all views

**Widget Dashboard**
```
┌──────────────┬──────────────┬──────────────────┐
│ CPU %        │ Memory       │ Network I/O      │
│ ▁▂▃▅▇█▇▅    │ [████░░] 60% │ ▲ 12MB ▼ 3MB    │
├──────────────┴──────────────┤                  │
│ Process List                │ Disk             │
│ ruby  12%  234MB            │ [██░░░░] 35%     │
└─────────────────────────────┴──────────────────┘
```
- Self-contained panels with independent data sources
- Braille/block characters for high-density in-cell charts

**Drill-Down Stack**
```
Cluster > Namespace > Pod > Container
[← Esc]  [← Esc]    [← Esc]
```
- Enter descends, Esc ascends
- Status bar shows breadcrumb trail
- `:resource` command mode for direct jumps

**IDE Three-Panel**
```
┌─────────┬──────────────────────────────────┐
│ Tree    │ Editor / Main                    │
│ lib/    │                                  │
│ ├app.rb │                                  │
│ └lib/   ├──────────────────────────────────┤
│         │ Output / REPL / Log              │
└─────────┴──────────────────────────────────┘
```
- Sidebar toggles with single key (e.g., `e`)
- Tab bar along top for open files / views
- Bottom panel height adjustable

**Overlay / Popup**
```
┌──────────────────────── Shell ─────────────────┐
│ $ git log                                       │
│                                                 │
│  ┌──────────── TUI Overlay ──────────────┐      │
│  │ > search query                        │      │
│  │   result 1                            │      │
│  │   result 2                            │      │
│  └───────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```
- Appears on demand over shell
- Configurable height (typically 40–60% of terminal)
- Returns selection to caller via stdout

**Header + Scrollable List**
```
┌─────────────────────────────────────────────────┐
│ CPU 23% | MEM 61% | [8 processes] | 14:22:01    │
├─────────────────────────────────────────────────┤
│ PID   NAME       CPU   MEM   STATUS             │
│ 1234  ruby       12%   234M  running            │
│ 5678  postgres    3%    87M  sleeping           │
│ ...                                             │
├─────────────────────────────────────────────────┤
│ q quit  / filter  s sort  k kill               │
└─────────────────────────────────────────────────┘
```
- Fixed header with live meters / stats
- Function bar at bottom (always visible)

### Responsive Strategies

Handle `Bubbletea::WindowSizeMessage` in the root App's update method.

| Terminal Width | Strategy |
|:---|:---|
| ≥ 120 cols | Full layout — all panels at configured widths |
| 80–119 cols | Proportional split — maintain percentage ratios |
| 60–79 cols | Priority collapse — hide least-important panel |
| < 60 cols | Stacking — panels collapse to title-only bars |
| < 40 cols | Gate — display "Terminal too narrow (min 80 cols)" |

**Minimum size convention:** 80×24. Test at 80×24, 120×40, 200×60.

---

## 2. Semantic Color System

Never hardcode hex values in component code. All colors flow through `Styles::COLORS`.

### Token Hierarchy

```ruby
# lib/[app_name]/styles.rb — COLORS hash (Layer 1)
COLORS = {
  # Foreground
  fg_default:   "#D8DEE9",   # body text
  fg_muted:     "#7B8394",   # secondary text, metadata, timestamps
  fg_emphasis:  "#FFFFFF",   # headers, focused items, titles
  fg_on_accent: "#000000",   # text rendered on accent background

  # Background
  bg_base:      "#1A1B26",   # primary app background (darkest)
  bg_surface:   "#24283B",   # panel / widget backgrounds
  bg_overlay:   "#2F3549",   # popup / dialog backgrounds
  bg_selection: "#364A82",   # selected item highlight

  # Accent
  accent_primary:   "#7AA2F7",  # interactive elements, focus borders
  accent_secondary: "#BB9AF7",  # supporting interactions, hints

  # Status (pair with symbols — never rely on color alone)
  status_error:   "#F7768E",  # ✗ error
  status_warning: "#E0AF68",  # ⚠ warning
  status_success: "#9ECE6A",  # ✓ success
  status_info:    "#7DCFFF"   # ℹ info
}.freeze
```

Style constants in Layer 2 consume tokens by key (plain hex strings — no `Color.new` wrapper):
```ruby
ACTIVE_PANEL = Lipgloss::Style.new
  .border(:rounded)
  .border_foreground(COLORS[:accent_primary])
  .padding(0, 1)
```

### Color Capability Detection

Detect before applying True Color palettes:

```ruby
def self.color_support
  return :none    if ENV["NO_COLOR"]
  return :true    if %w[truecolor 24bit].include?(ENV["COLORTERM"])
  return :c256    if ENV["TERM"]&.include?("256color")
  :ansi16
end
```

| Level | Fallback Strategy |
|:---|:---|
| `:true` | Use full COLORS hex palette |
| `:c256` | Map tokens to nearest xterm-256 index |
| `:ansi16` | Map tokens to nearest ANSI color name |
| `:none` | Strip all color; rely on bold/dim/underline only |

**Golden rule:** The TUI must be *usable* in 16-color mode. True Color *enhances* — it never *creates* hierarchy.

### Visual Hierarchy Without Color

Use SGR attributes alongside (or instead of) color:

| Attribute | Use For |
|:---|:---|
| Bold (SGR 1) | Headers, labels, active items |
| Dim (SGR 2) | Metadata, timestamps, unfocused panels |
| Italic (SGR 3) | Comments, type hints, annotations |
| Underline (SGR 4) | Links, clickable elements |
| Reverse (SGR 7) | Selection highlight (works in all modes) |
| Strikethrough (SGR 9) | Deleted items, deprecated entries |

### Background Layering

Each background tier is ~5–8% lighter than the previous in dark themes:

```
bg_base (darkest) → bg_surface → bg_overlay (lightest)
```

Modals and dialogs use `bg_overlay`; main app body uses `bg_base`.

---

## 3. Keyboard Architecture

Every app should implement exactly the layers it needs — no more.

### Four-Layer Model

| Layer | Keys | Trigger | Always Visible? |
|:---|:---|:---|:---|
| **L0 Universal** | Arrows, Enter, Esc, q, Tab, Shift+Tab | All apps | Yes — footer |
| **L1 Vim Motions** | hjkl, gg, G, /, ?, : | Navigation-heavy apps | Yes — footer |
| **L2 Actions** | Domain mnemonics (d, n, e, p…) | Regular users | On `?` help |
| **L3 Power** | Composed commands, command palette | 20+ action apps | Docs only |

### Standard Key Conventions

```
j / ↓       cursor down          g / Home    jump to top
k / ↑       cursor up            G / End     jump to bottom
h / ←       collapse / back      /           open search
l / → / Enter  expand / forward  ?           toggle help overlay
Tab         focus next panel     :           command mode
Shift+Tab   focus prev panel     q / Esc     quit / back
Space       toggle selection     n / N       next / prev match
```

### Key Conflict Resolution

- `h` in L1 (collapse/back) takes priority over `h` as a domain mnemonic
- Never use `h` for "help" — remap help to `?`
- `q` (quit) is L0 — never reassign it to a domain action
- If a domain action must use a reserved key, use uppercase or `ctrl+` variant

### Keyboard Layer Architecture (Ruby)

```ruby
# lib/[app_name]/components/keyboard.rb
module Components::Keyboard
  L0 = {
    up:        :cursor_up,      down:      :cursor_down,
    left:      :focus_prev,     right:     :focus_next,
    enter:     :confirm,        escape:    :cancel_or_back,
    tab:       :focus_next_panel,
    shift_tab: :focus_prev_panel,
    "q":       :quit
  }.freeze

  L1 = {
    "j": :cursor_down,  "k": :cursor_up,
    "h": :collapse_or_back, "l": :expand_or_forward,
    "g": :goto_top,     "G": :goto_bottom
  }.freeze

  L2 = {}.freeze  # populate per-domain (e.g., "n" => :new_item)

  def self.resolve(key, layers: [:l0])
    { l0: L0, l1: L1, l2: L2 }.slice(*layers).each_value do |map|
      msg = map[key.to_sym]
      return msg if msg
    end
    nil
  end
end
```

Usage in app's update method:
```ruby
when Bubbletea::KeyMessage
  if (action = Components::Keyboard.resolve(message.to_s, layers: [:l0, :l1]))
    dispatch_action(action, state)
  end
```

---

## 4. Three-Tier Help System

### Tier 1 — Always-Visible Footer (3–5 keys)

Show the most critical bindings at all times. Use `Bubbles::Help` (see tui-patterns.md §Bubbles::Help):

```ruby
def footer_view
  bindings = [
    Bubbles::Key.binding(keys: ["q"],     help: ["q", "quit"]),
    Bubbles::Key.binding(keys: ["?"],     help: ["?", "help"]),
    Bubbles::Key.binding(keys: ["tab"],   help: ["tab", "focus"]),
    Bubbles::Key.binding(keys: ["/"],     help: ["/", "search"])
  ]
  help = Bubbles::Help.new
  help.short_help_view(bindings)
end
```

Surface this in the root App's `view` method between content and bottom edge.

### Tier 2 — On-Demand `?` Overlay

Full keybinding reference for the current context. Rendered as a modal over the active view:

```ruby
# In root app's update:
in "?"
  state.merge(show_help: !state.show_help)

# In view:
if state.show_help
  help_content = render_help_overlay(state.active_screen)
  Components::Base.join_vertical(main_view, help_content)
else
  main_view
end
```

Help overlay should be context-sensitive — show bindings for the **currently focused panel**, not all bindings globally.

### Tier 3 — Documentation

External `--help` flag or README. Not rendered inside the TUI. Reference to offline docs is sufficient.

---

## 5. Focus Management

### Tab Order and Visual Feedback

- `Tab` cycles forward through focusable panels
- `Shift+Tab` cycles backward
- Focused panel: rendered with `ACTIVE_PANEL` style (accent border)
- Unfocused panels: rendered with `Components::Base.focus_dim(content)` (muted text)

Track focus as a Symbol key in state:

```ruby
State = Struct.new(:focused_panel, :panels, keyword_init: true)
# focused_panel: :sidebar | :main | :log

# In view:
panels.each do |name, content|
  if name == state.focused_panel
    Components::Base.active_panel(content)
  else
    Components::Base.focus_dim(content)
  end
end
```

### Modal Focus Traps

While a modal / overlay is visible, Tab must not escape to background panels:

```ruby
in "tab"
  if state.modal_open
    state.merge(modal_focus: next_modal_field(state.modal_focus))
  else
    state.merge(focused_panel: next_panel(state.focused_panel))
  end
```

Modal background panels should be rendered through `focus_dim` to signal they are inactive.

---

## 6. Command Palette Pattern

Use when the app has **20 or more user-visible actions**.

### Trigger and Architecture

- Open: `ctrl+p`
- Close: `Esc`
- All action methods in the app carry an `action_` prefix
- The palette discovers them via `respond_to?` and `method_name.start_with?("action_")`

```ruby
# In root App:
def action_new_file      = dispatch(:new_file)
def action_delete_item   = dispatch(:delete_item)
def action_export_csv    = dispatch(:export_csv)
# ...

# Palette discovery:
available_actions = methods.select { |m| m.to_s.start_with?("action_") }
                           .map { |m| m.to_s.delete_prefix("action_").tr("_", " ") }
```

### Fuzzy Matching

```ruby
module FuzzyMatcher
  def self.score(query, candidate)
    return 0 if query.empty?
    q = query.downcase
    c = candidate.downcase
    return 100 if c.include?(q)          # substring match

    i = 0
    score = 0
    c.each_char do |ch|
      if i < q.length && ch == q[i]
        score += 10
        i += 1
      end
    end
    i == q.length ? score : 0            # 0 if not all chars matched
  end

  def self.rank(query, candidates)
    candidates
      .map { |c| [c, score(query, c)] }
      .select { |_, s| s > 0 }
      .sort_by { |_, s| -s }
      .map(&:first)
  end
end
```

Use `Bubbles::TextInput` for the palette input field (see tui-patterns.md §Bubbles::TextInput).

---

## 7. Anti-Pattern Checklist

Review generated code against these before output. Ranked by frequency of complaint.

| # | Anti-Pattern | Fix |
|:---|:---|:---|
| 1 | Hardcoded hex in component files | Route all color through `Styles::COLORS` tokens |
| 2 | `puts` / `print` called per-frame in `view` | Use Lipgloss rendering only; no stdout in view |
| 3 | Keybindings undiscoverable | Footer shows 3–5 keys; `?` reveals full overlay |
| 4 | Mutable state in `view` method | View is pure; all state changes go through update |
| 5 | Unconstrained panel width | Set explicit `max_width` or proportional constraints |
| 6 | Blocking I/O in `update` | Async all external calls; show spinner while pending |
| 7 | Direct Lipgloss calls in screen/component files | All rendering through `Components::Base` adapter |
| 8 | Inline style strings in `view` | All styles as named constants in `Styles` module |
| 9 | Focus state derived from `view` | Focus is explicit state field, never inferred from display |
| 10 | No resize handler | Handle `Bubbletea::WindowSizeMessage`; reflow layout |

---

## 8. Compatibility Checklist

Verify before marking a scaffold complete.

**Terminal Size**
- [ ] Minimum 80×24 — show "Terminal too narrow" message below threshold
- [ ] Handles `Bubbletea::WindowSizeMessage` without crashing
- [ ] Layout reflows gracefully on resize

**Color & Accessibility**
- [ ] Detects `$NO_COLOR` and strips ANSI; TUI remains usable
- [ ] Tested on both dark and light terminal backgrounds
- [ ] Never relies on color alone — pair with symbols, text, or position
- [ ] Avoids red/green distinction as sole signal (colorblindness)

**Terminal Compatibility**
- [ ] Works inside tmux and zellij (avoid raw mouse without bubblezone guard)
- [ ] Functions over SSH (no True Color assumption without `$COLORTERM` check)
- [ ] Mouse capture does not break text selection when bubblezone is inactive
- [ ] No ANSI escape leaks when stdout is piped (non-TTY check)

**Keyboard**
- [ ] Every feature reachable via keyboard alone
- [ ] L0 bindings (arrows, Enter, Esc, q) active in all contexts
- [ ] `?` help overlay documents context-specific bindings
- [ ] No `ctrl+c` override — exits cleanly on `SIGINT`

**Elm Architecture Purity**
- [ ] `view` is a pure function: no I/O, no side effects, no state mutation
- [ ] `update` returns new state — never mutates existing state
- [ ] No `Thread.new` inside update or view; async via `Async { }` in commands
