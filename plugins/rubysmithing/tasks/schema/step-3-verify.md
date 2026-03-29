# Schema — Step 3: Implementation Verification

You are the `senior-qa-engineer` executing Step 3 of the `/rubysmithing:schema` workflow.

## Your Input

The schema and pipeline artifacts produced in Step 2.

## Your Task

Run a scoped SIFT assessment focused on data infrastructure correctness and SFL architectural compliance.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/sift/SKILL.md`
2. Load `$CLAUDE_PLUGIN_ROOT/skills/sift/references/sift-protocol.md`
3. Run in Tech Advisory mode (condensed) unless the output is 3+ files or involves Neo4j dual-write
4. Focus on these data-layer dimensions in addition to standard SIFT checks:

### Embedding Consistency
- `vector(N)` column size matches the declared backend: `informers/all-MiniLM-L6-v2`=384, `nomic-embed-text-v1`=768, OpenAI=1536
- All `embedding` columns in the same table use identical dimensions

### Idempotency
- `content_hash` (SHA256) column present on every text-bearing table (`sentences`, `clauses`)
- `unique: true` constraint on `content_hash`
- Redis idempotency key checked before PostgreSQL insert in pipeline code

### SFL Schema Correctness
- `process_type` enum constraint includes all 6 valid types: `material`, `mental`, `relational`, `verbal`, `behavioural`, `existential`
- `mood_type` enum constraint includes: `declarative`, `interrogative`, `imperative`, `exclamative`, `minor`
- `participants.role` enum includes the polymorphic set: `actor`, `goal`, `beneficiary`, `senser`, `phenomenon`, `sayer`, `verbiage`, `receiver`, `carrier`, `attribute`, `token`, `value`, `behaver`, `existent`
- `register_metadata` JSONB on `documents` table contains `field`, `tenor`, `mode` keys (not on `clauses`)
- Clause Complex adjacency list: `parent_complex_id` self-referencing FK on `clauses`

### Index Strategy
- HNSW index present on every `embedding` column (`vector_cosine_ops` op class)
- GIN index present on every JSONB column used in filter queries (`ideational_structure`, `interpersonal_structure`, `thematic_structure`, `register_metadata`)
- `process_type` and `mood_type` plain B-tree indexes present (used in WHERE clause routing)
- `pg_trgm`, `uuid-ossp`, and `vector` extensions bootstrapped at migration start

### JSONB Validation
- `dry-schema` contract present for each JSONB column (or `[WARNING: missing contract]` acknowledged)
- `ideational_structure` contract covers: `participants` array with `role`, `text`, `token_indices`; `circumstances` array with `type`, `text`

### Fallback / Degradation
- Hybrid retriever has symbolic-only fallback path (process_type/mood WHERE clause) when embedding unavailable
- Circuit breaker present on remote embedding API calls (not required for local `informers`)

### Transactional Outbox (if Neo4j present)
- `graph_sync_outbox` table present with `event_type`, `payload JSONB`, `status`, index on `status`
- Clause insert wrapped in `DB.transaction` with simultaneous outbox event insert
- Neo4j worker uses `MERGE` not `CREATE`

5. Cite named patterns from `$CLAUDE_PLUGIN_ROOT/skills/refactor/references/refactor-patterns.md` for any recommended fixes.

## Output

```
SCHEMA VERIFICATION
Mode: Tech Advisory | Full SIFT
Artifacts reviewed: N

CRITICAL (blocks merge): [file:line — issue]
WARNING (should address): [file:line — issue]
CLEAN: [dimension — evidence]

SFL DATA-LAYER CHECKS:
  Embedding consistency:     PASS | FAIL — <model name, declared dim, column dim>
  Idempotency (content_hash): PASS | FAIL — <table names checked>
  process_type enum:         PASS | FAIL — <6 types present?>
  participants.role enum:    PASS | FAIL — <polymorphic set present?>
  HNSW index:                PASS | FAIL — <tables checked>
  GIN indexes:               PASS | FAIL — <JSONB columns checked>
  pg_trgm / uuid-ossp:       PASS | FAIL | N/A
  dry-schema contracts:      PASS | FAIL | MISSING — <columns>
  Fallback path:             PASS | FAIL | N/A — <evidence>
  Transactional Outbox:      PASS | FAIL | N/A — <MERGE idempotency?>

VERDICT: SHIP | NEEDS FIXES
```
