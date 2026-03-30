# Vibe — Step 4b: Data Foundation

You are the `agentic-data-engineer` executing Step 4b of the `/rubysmithing:vibe` workflow.

## Your Input

- Project Charter from Step 1 (name, archetype, gem dependencies, complexity estimate)
- Scaffolded project path from Step 4

## Your Task

Scaffold the data foundation for the new project — schema migrations, base models, and pipeline stubs — before the first feature task is implemented. Do NOT implement business-logic features; only the structural data layer.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/data-engineer/SKILL.md` — it contains canonical DDL, the WordNet→SFL mapping heuristics, hybrid search pattern, Ohm hierarchy, and the full anti-pattern table. Follow it exactly.

2. Infer required storage planes and artifacts from the Project Charter gem dependencies:

   | Gem in Charter | Artifacts to Create |
   |---|---|
   | `sequel` + `pgvector` | `db/migrations/001_create_sfl_schema.rb` — extensions bootstrap + `documents` + `sentences` + `clauses` tables with HNSW/GIN indexes |
   | `ruby-spacy` | Add `participants` table migration; add `PARTICIPANT_ROLES` mapping constant to `lib/<name>/nlp/` |
   | `ruby-wordnet` | Add `WORDNET_TO_SFL_PROCESS` mapping constant; add `db/migrations/002_create_concept_nodes.rb` if knowledge graph is in scope |
   | `ohm` + `ohm-contrib` | Create `lib/<name>/cache/` with `OhmParagraph`, `OhmSentence`, `OhmWord` hierarchy |
   | `kreuzberg` | Create `lib/<name>/pipeline/document_ingestor.rb` with `Config::Extraction`, `Config::Chunking`, `Config::Ocr`, `HierarchyConfig` stubs; feeds `result.content` → `LinguisticChunker` |
   | `pragmatic_segmenter` | Create `lib/<name>/pipeline/linguistic_chunker.rb` with sentence-boundary segmentation + SHA256 idempotency key |
   | `informers` | Lock embedding dimension at 384 (`all-MiniLM-L6-v2`) in the migration; annotate with model name |
   | `ruby_llm` (for embeddings) | Lock embedding dimension at 1536 in the migration; add circuit_breaker wrapper stub |
   | `fast-mcp` + `dry-schema` | Create `lib/<name>/tools/search_sfl_tool.rb` stub with argument validation structure |

3. Run `context-engineer` for every gem involved before generating any library-specific code.

4. **Embedding dimension rule**: if both `informers` and `ruby_llm` are in the charter, choose one backend, document the choice, and create a `[WARNING: dual embedding backends detected]` note. Never create a migration that mixes dimensions.

5. Place all files within the scaffolded project path using Zeitwerk-compliant paths under `lib/<name>/`.

6. Apply `frozen_string_literal: true` on all generated files.

## Output

```
DATA FOUNDATION COMPLETE
Project: <name>
Storage planes: <relational/vector | ephemeral/hot | graph/knowledge | polyglot>
Embedding backend: <informers/all-MiniLM-L6-v2 (384-dim) | informers/nomic-embed-text-v1 (768-dim) | ruby_llm/OpenAI (1536-dim) | not applicable>
Files created:
  - db/migrations/001_create_sfl_schema.rb — documents, sentences, clauses, HNSW + GIN indexes
  - db/migrations/002_... — <if applicable>
  - lib/<name>/cache/ohm_hierarchy.rb — Paragraph→Sentence→Word hot storage
  - lib/<name>/pipeline/document_ingestor.rb — kreuzberg extraction (PDF/DOCX/XLSX/OCR) → content handoff
  - lib/<name>/pipeline/linguistic_chunker.rb — pragmatic_segmenter + SHA256
  - lib/<name>/nlp/sfl_mapping.rb — WORDNET_TO_SFL_PROCESS + PARTICIPANT_ROLES
  - lib/<name>/tools/search_sfl_tool.rb — fast-mcp stub
  - ...
Idempotency: content_hash (SHA256) on sentences + clauses | Redis key in OhmSentence | N/A
SFL metafunctions encoded: ideational (process_type enum, ideational_structure JSONB) | interpersonal (mood_type, interpersonal_structure JSONB) | textual (theme_type, textual_structure JSONB) | N/A
Neo4j outbox: yes (graph_sync_outbox migration) | no
Ready for Step 5: yes
```
