# TUI Design Patterns (Gum/Bash)

Design system reference for bashsmithing TUI projects. Framework-agnostic principles
distilled to the gum/bash context. See `SKILL.md` for code generation workflow.

---

## 1. Layout Paradigm Guide

Choose a paradigm before designing the skeleton — each has a different structural contract.

### Main Menu Loop

```
┌─ App Title ─────────────────────────┐
│                                     │
│  > Action One                       │
│    Action Two                       │
│    Action Three                     │
│    Quit                             │
│                                     │
└─────────────────────────────────────┘
[q]uit  [Enter]select
```

**Use for:** Single-purpose tools with fewer than ~20 actions. The canonical bashsmithing entry point.
**State model:** Flat — `while true` loop, `case` dispatch, no navigation history.
**Key rule:** Include a `Press Enter to continue...` pause after each action so output is readable before the menu redraws.

---

### Persistent Multi-Panel

```
┌─ Nav ──────┬─────────── Detail ──────────┐
│ > item-1   │  Contents of item-1...      │
│   item-2   │                             │
│   item-3   │                             │
├────────────┤                             │
│ [Status]   │                             │
└────────────┴─────────────────────────────┘
[q]uit  [Tab]focus  [?]help
```

**Use for:** Multi-context tools where users need simultaneous views (git-like clients, monitoring dashboards, container managers).
**State model:** Focus variable tracks active panel; `Tab` rotates focus; each panel is a string block composed via `gum join`.
**Key rule:** Panels maintain fixed positions. Never rearrange layout without explicit user action — users build spatial memory ("left panel is always navigation").

---

### Drill-Down Stack

```
home > environments > production > services
┌─────────────────────────────────────┐
│  production / services              │
│  > api-server                       │
│    worker                           │
│    scheduler                        │
└─────────────────────────────────────┘
[Esc]back  [Enter]drill-in  [q]quit
```

**Use for:** Hierarchical data navigation (Kubernetes resources, nested configs, file browsers).
**State model:** Array-based screen stack — `Nav::push` on enter, `Nav::pop` on `Esc`. Always render breadcrumb.
**Key rule:** `Enter` descends, `Esc` ascends. If the stack depth exceeds ~5 levels, add a `:path/to/resource` direct-jump command mode.

---

### Overlay/Popup

Called by another script. Renders over the existing terminal state, returns a value, exits.

**Use for:** Shell augmentations — file pickers, history search, fuzzy selectors invoked from other tools.
**State model:** Stateless — single interaction, stdout result.
**Key rule:** Never disrupt scrollback. Output selection to stdout only. Configurable height via `--height` flag.

---

### Header + Scrollable List

```
┌─ CPU: 45%  MEM: 67%  DISK: 23%  ────┐
├──────────────────────────────────────┤
│  PID   NAME        CPU%   MEM%       │
│> 1234  postgres    23.4   4.5        │
│  5678  node        12.1   8.3        │
│  9012  redis        2.3   1.1        │
└──────────────────────────────────────┘
[q]quit  [/]search  [k]kill  [r]refresh
```

**Use for:** Single-list tools with metadata — process viewers, log viewers, sorted listings.
**State model:** Refresh loop updates header data; list is re-piped to `gum filter` or `gum table` each cycle.
**Key rule:** Sort by the most actionable dimension by default. Header creates natural "overview then detail" reading flow.

---

## 2. Responsive Terminal Design

Terminals resize. Handle it in every scaffold:

| Strategy | When |
|:---------|:-----|
| Proportional split | Panels maintain percentage ratios on resize (use `gum join` fractional via `--width`) |
| Priority collapse | Narrow terminal → hide secondary panels, keep primary content |
| Minimum size gate | Below 80×24, display `"Terminal too small — resize to 80×24 minimum"` and exit |

**Rules:**
- Define minimum terminal size: 80 columns × 24 rows
- Never crash on resize — trap `SIGWINCH` if using a refresh loop
- Use `tput cols` / `tput lines` to check dimensions at startup

---

## 3. Interaction Model

### Navigation by Complexity

| App Complexity | Recommended Model |
|:---------------|:-----------------|
| Single-purpose, <20 actions | Direct keybinding (every key = action) |
| Multi-view, complex | Vim-style modes + contextual footer |
| Many features | Command palette (gum filter over all actions) + footer |
| Data browser | Drill-down + `/` fuzzy search + `:` command mode |

### Keyboard Lingua Franca

Adhere to these conventions to avoid surprising users:

| Key | Action |
|:----|:-------|
| `j` / `k` | Move down / up |
| `h` / `l` | Move left / right (or collapse / expand) |
| `/` | Enter search mode |
| `?` | Help overlay |
| `:` | Command mode |
| `q` | Quit (or close sub-screen) |
| `Esc` | Go back one level |
| `Enter` | Select / confirm / drill in |
| `Tab` | Switch focus between panels |
| `Space` | Toggle selection |
| `g` / `G` | Jump to top / bottom |

**Never bind:** `Ctrl+C` (interrupt), `Ctrl+Z` (suspend), `Ctrl+\` (quit signal) — these belong to the terminal.

### Focus Management

- Only one panel/widget receives keyboard input at a time
- `Tab` cycles focus forward; `Shift+Tab` backward
- Focused panel: highlighted border or color change
- Unfocused panels: dimmed border (use `$GUM_COLOR_MUTED`)
- Modal dialogs trap focus — background receives no events until resolved

### Search Pattern

Standard: press `/`, type, results filter live.

```bash
Search::open() {
  local -a items=("$@")
  printf '%s\n' "${items[@]}" \
    | gum filter \
        --placeholder "Search..." \
        --indicator "▶" \
        --match.foreground "${GUM_COLOR_PRIMARY}"
}
```

---

## 4. Help System — Three Tiers

| Tier | Trigger | Content |
|:-----|:--------|:--------|
| **Always visible** | Footer bar (every screen) | 3–5 essential shortcuts for current context |
| **On demand** | `?` key | Full keybinding list via `gum pager` |
| **Documentation** | `--help` flag | Complete reference, printed to stdout |

**Footer format rule:** Show only what is actionable *right now*. Update per active screen.

```
[q]uit  [/]search  [?]help  [Tab]focus  [Enter]select
```

---

## 5. Semantic Color System

### Color Tier Detection

```bash
if [[ "${COLORTERM:-}" == "truecolor" || "${COLORTERM:-}" == "24bit" ]]; then
  BASHSMITH_COLOR_TIER=truecolor
elif [[ "${TERM:-}" == *256color* ]]; then
  BASHSMITH_COLOR_TIER=256
else
  BASHSMITH_COLOR_TIER=16
fi
```

**Golden rule:** Your TUI must be *usable* in 16-color ANSI mode. True color *enhances*, never *creates*, the hierarchy.

### Semantic Slot Table

| Slot | Variable | Default (256) | Purpose |
|:-----|:---------|:-------------|:--------|
| Primary accent | `GUM_COLOR_PRIMARY` | 212 | Interactive elements, focus indicator |
| Secondary accent | `GUM_COLOR_SECONDARY` | 57 | Supporting interactions |
| Success | `GUM_COLOR_SUCCESS` | 82 | Positive outcomes, additions |
| Error | `GUM_COLOR_ERROR` | 196 | Failures, deletions |
| Warning | `GUM_COLOR_WARNING` | 214 | Caution, non-fatal issues |
| Muted | `GUM_COLOR_MUTED` | 240 | Metadata, timestamps, footer text |

Always reference slot variables — never hardcode `212` or `#d787ff` in widget code.

### Visual Hierarchy Recipe

80% of content in default terminal foreground. Use these sparingly:
- **Bold** — headers, active items, labels
- **Dim** (`gum style --faint`) — metadata, timestamps, secondary info
- **Color** — semantic slots only; never decorative

---

## 6. Accessibility Requirements

- **WCAG AA contrast**: 4.5:1 for body text, 3:1 for large UI elements
- **Never color-only signals**: Pair every status color with a symbol (✓ ✗ ⚠ •) and text
- **`NO_COLOR` support**: When set, unset all `GUM_COLOR_*` vars — the TUI must remain usable
- **Color-blindness safe pairs**: blue+orange, blue+yellow, black+white — avoid red-vs-green as the sole distinction

---

## 7. The Seven Design Principles

1. **Keyboard-first, mouse-optional** — Every feature accessible via keyboard. Mouse enhances, never replaces.

2. **Spatial consistency** — Panels stay in fixed positions. Users build mental maps. Never rearrange without explicit user action.

3. **Progressive disclosure** — Show 3–5 essential shortcuts in the footer. Full help behind `?`. Complete reference in `--help`. The floor is accessible; the ceiling is unlimited.

4. **Async everything** — Never freeze the UI. File operations, network requests, and external commands all run inside `Gum::spin`. Cancel with `Esc`.

5. **Semantic color** — Color encodes meaning, not decoration. If you removed all color, the interface must still be *usable* through layout, symbols, and text.

6. **Contextual intelligence** — Footers update per active panel. Status bars reflect current state. Help shows what's actionable *right now*, not everything ever.

7. **Design in layers** — Start with no color (usable?). Add 16 ANSI (readable?). Layer 256/true color (beautiful?). Each tier must stand independently.

---

## 8. Anti-Pattern Checklist

Ordered by real-world complaint frequency:

| # | Anti-Pattern | Fix |
|:--|:-------------|:----|
| 1 | Colors break on different terminals | Use 16 ANSI as foundation; test on 3+ emulators in light and dark themes |
| 2 | Flickering / unnecessary redraws | Use `clear` only at menu top; never clear mid-action |
| 3 | Undiscoverable keybindings | Context-sensitive footer + `?` overlay on every screen |
| 4 | No `NO_COLOR` support | Guard all color vars; test with `NO_COLOR=1 ./bin/run` |
| 5 | Blocking UI during operations | Wrap all external commands in `Gum::spin` |
| 6 | Modal confusion | Always echo current mode or screen name in header/breadcrumb |
| 7 | Color as sole status signal | Pair with symbol (✓ ✗ ⚠) and text label |
| 8 | Unquoted `gum join` variables | Always quote: `gum join "$A" "$B"` — unquoted drops newlines |
| 9 | No gum-absent fallback | `read`-based fallback in every interactive function |
| 10 | Over-decorated chrome | Borders and color serve content; content *is* the interface |

---

## 9. Compatibility Checklist

Before outputting any scaffold, verify the generated code:

- [ ] Works at 80×24 minimum terminal size (check with `tput cols` / `tput lines`)
- [ ] Handles terminal resize without crash (`SIGWINCH` trap if using refresh loop)
- [ ] Respects `NO_COLOR` — all `GUM_COLOR_*` vars guarded
- [ ] All features accessible via keyboard alone
- [ ] `Gum::catch_ctrlc` trap present in every entry point with a loop
- [ ] No ANSI escape leaks when stdout is piped or redirected
- [ ] Exits cleanly on `Ctrl+C` / `SIGINT` — terminal state restored
- [ ] Works over SSH (no local-only protocol dependencies)
- [ ] Tested without gum installed (read-based fallback activates)
- [ ] Bootstrap guard `[[ "${BASH_SOURCE[0]}" == "${0}" ]]` in every lib file
