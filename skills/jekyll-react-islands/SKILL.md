---
name: jekyll-react-islands
description: Workflows for Jekyll static sites with React island architecture. Handles component creation, content management, themes, and build processes.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.0.0"
  category: developer-tools
---

# Jekyll + React Island Architecture Skill

This skill provides workflows for working with a Jekyll-based static site enhanced with React island architecture for progressive interactivity.

## Architecture Overview

The project uses a **dual-pipeline build**:
- **Jekyll (Ruby)**: Generates static HTML from Markdown, JSON, and Liquid templates
- **esbuild/Tailwind (Node)**: Bundles React components and compiles CSS

**Island Architecture Pattern**: Static HTML is generated first, then React hydrates specific interactive "islands" marked with `data-island` attributes. This ensures fast initial loads, SEO-friendly content, and progressive enhancement.

## Project Structure

```
b08x.github.io/
├── _config.yml              # Jekyll configuration, collections, plugins
├── package.json             # Node dependencies and npm scripts
├── Gemfile                  # Ruby dependencies
├── src/
│   ├── main.tsx             # React island hydration entry point
│   ├── components/          # React island components (23 components)
│   └── utils/               # Theme sync utilities
├── _plugins/                # Custom Ruby plugins (11 plugins)
├── _layouts/                # Jekyll HTML templates (15 layouts)
├── _includes/               # Reusable HTML partials
├── _notes/                  # Digital garden markdown content
├── _data/wikis/             # Wiki source JSON files
├── _sass/                   # SCSS theme system
└── assets/
    ├── js/dist/             # esbuild output (garden-widgets-v2.js)
    └── css/compiled.css     # Tailwind CSS output
```

## Core Concepts

### Island Hydration System

React components are mounted via `data-island` and `data-props` attributes:

```html
<div data-island="ComponentName" data-props='{"prop": "value"}'></div>
```

The `mountIslands()` function in `src/main.tsx`:
1. Scans DOM for `[data-island]` elements
2. Parses `data-props` (JSON or Base64-encoded JSON)
3. Lazy-loads the component via `React.lazy()`
4. Hydrates with `createRoot()`

### Theme System

- **CSS Variables**: Defined in `_sass/_theme-variables.scss`
- **Tailwind Mapping**: Variables mapped in `tailwind.config.js`
- **React Sync**: Components use `MutationObserver` watching `document.documentElement.classList`
- **CSS Variables**: Use `var(--foreground)`, `var(--accent)`, etc. — never hardcode colors

### Auto-Enhancement Pipelines

Static content is automatically converted to React islands:
- Rouge code blocks → `CodeBlock` component
- Mermaid images → `MermaidViewer` component
- Picture tags with lightbox → `ImageLightbox` component

## Common Workflows

### Adding a New React Island Component

1. **Create the component** in `src/components/MyComponent.tsx`:
   ```typescript
   import React from 'react';
   
   interface MyComponentProps {
     title: string;
     data?: string[];
   }
   
   const MyComponent: React.FC<MyComponentProps> = ({ title, data = [] }) => {
     // Use CSS variables for theming: var(--foreground), var(--accent), etc.
     return (
       <div style={{ color: 'var(--foreground)' }}>
         <h1>{title}</h1>
         {data.map(item => <div key={item}>{item}</div>)}
       </div>
     );
   };
   
   export default MyComponent;
   ```

2. **Register in `src/main.tsx`**:
   ```typescript
   const MyComponent = React.lazy(() => import('./components/MyComponent'));
   const components = {
     // ...existing components
     MyComponent,
   };
   ```

3. **Build the bundle**: `npm run build:js`

4. **Use in Jekyll templates or content**:
   ```liquid
   {% assign props = '{"title": "Hello", "data": ["a", "b"]}' | jsonify %}
   <div data-island="MyComponent" data-props='{{ props }}'></div>
   ```

### Adding New Note Content

1. Create markdown file in `_notes/`
2. Add front matter:
   ```yaml
   ---
   title: My Note
   date: 2024-01-01
   tags: [tag1, tag2]
   ---
   ```
3. Use `[[wikilink]]` syntax for internal links (processed by `bidirectional_links_generator.rb`)

### Adding Wiki Content

1. Add JSON to `_data/wikis/wiki-name.json`:
   ```json
   {
     "metadata": { "repository": "...", "generated_at": "..." },
     "pages": [
       { "id": "page-1", "title": "Page Title", "content": "Markdown content", "importance": "high" }
     ]
   }
   ```
2. Run `npm run build:jekyll` to regenerate pages
3. Wiki pages go to `/wikis/:slug` (generated, don't edit directly)

### Using Jekyll Plugins

Key plugins in `_plugins/`:
| Plugin | Purpose |
|--------|---------|
| `wiki_page_generator.rb` | Generates paginated wiki from JSON |
| `bidirectional_links_generator.rb` | `[[wikilink]]` → `<a>` + backlinks |
| `obsidian_callouts.rb` | `> [!type]` → HTML callouts |
| `render_liquid.rb` | Renders Liquid within JSON/strings |

## Build Commands

```bash
# Development (concurrent)
npm run dev                    # watch:js + dev:jekyll parallel

# Build all
npm run build                  # build:js + build:worker + build:css + build:jekyll

# Individual builds
npm run build:js               # esbuild → assets/js/dist/garden-widgets-v2.js
npm run build:worker           # esbuild → assets/js/dist/graph.worker.js
npm run build:css              # tailwindcss → assets/css/compiled.css
npm run build:jekyll           # jekyll clean && jekyll build

# Jekyll only
npm run dev:jekyll             # jekyll serve --incremental
```

## Debugging

- **Browser Console**: Look for `[Garden]` prefix — shows mount/render status
- **Dev Server**: `http://localhost:4000`
- **Theme Toggle**: Test in both dark and light modes

## Anti-Patterns to Avoid

- **NEVER** edit `_wikis/` directly — generated from `_data/wikis/*.json`
- **NEVER** commit `assets/js/dist/` — build artifacts (862+ chunks)
- **NEVER** commit `assets/img/generated/` — build artifacts
- **NEVER** use synchronous imports in `src/main.tsx` — use `React.lazy()`
- **NEVER** hardcode colors in components — use CSS variables
- **NEVER** use `innerHTML` with user content — XSS risk
- **NEVER** edit compiled CSS (`compiled.css`) or built JS directly
- **NEVER** suppress type errors with `as any`, `@ts-ignore`

## Key Files Reference

| Task | Location |
|------|----------|
| Add React component | `src/components/` + register in `src/main.tsx` |
| Modify wiki pagination | `_plugins/wiki_page_generator.rb` |
| Add wiki content | `_data/wikis/{wiki-id}.json` then `jekyll build` |
| Edit note layout | `_layouts/note.html` |
| Theme variables | `_sass/_theme-variables.scss` + `tailwind.config.js` |
| Syntax highlighting | `src/utils/syntaxTheme.ts` |

## Available Components

| Component | Purpose |
|-----------|---------|
| `PromptFlowDiagram` | YAML-driven prompt flow visualizer |
| `JsonCanvasViewer` | Canvas file visualization with D3 |
| `KnowledgebaseCarousel` | H2-based content carousel |
| `VideoPlayer` | HLS video with segments |
| `CodeBlock` | Syntax highlighting + copy |
| `GraphView` | D3 force-directed graph |
| `MermaidViewer` | Interactive diagrams |
| `NotesGrid` | Grid display with detail view |
| `SearchCmdK` | Command palette (Cmd/Ctrl+K) |
| `AudioPlayer` | Audio with waveform |

---

For component-specific patterns, refer to `src/components/AGENTS.md`.
