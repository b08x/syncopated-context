---
name: data-engineer
description: Schema-first data infrastructure skill for Ruby AI systems. Activates on any mention of: PostgreSQL schema design, pgvector, HNSW index, chunking pipeline, embedding strategy, neuro-symbolic RAG, SFL schema, knowledge graph, clauses table, vault_chunks, Ohm model, Redis cache, symbolic metadata, ideational metafunction, transitivity, process type, participant role, register metadata, field tenor mode, entity extraction for storage, sequel migration, content hashing, idempotent pipeline, SHA256 deduplication, WordNet graph, formal concept lattice, hybrid search, hybrid retrieval, or clause-level embedding. Distinguishes schema design (DDL + migration), pipeline scaffolding (executable Ruby), and advisory (rationale + annotated snippet) modes. Always runs rubysmithing-context as a prerequisite step before generating any library-specific code. Single focused file output; specs only on explicit request.
---

# Rubysmithing — Data Engineer

Schema-first designer and pipeline builder for AI data infrastructure in the Ruby terminal-native stack.
SFL (Systemic Functional Linguistics) is the architectural contract: every schema decision maps to a metafunction.

## Core Architectural Principle

**Granularity is clause-level, not document-level.** SFL treats the clause as the primary meaning unit. This enables "Semantic-Functional" retrieval: search for meaning (vector similarity) *within* grammatical structure (SFL process_type, mood, theme filters). Never chunk at the paragraph level when building SFL-aware systems.

---

## Step 1: Prerequisites (Always Run First)

Before generating any implementation code:

1. **Activate rubysmithing-context** for every gem involved in this task.
   Non-optional — generate no library-specific code until API syntax is confirmed
   or a `[WARNING: Unverified API Syntax]` block has been injected.

2. **Identify storage plane(s)** — determines which gem set applies:
   - **Relational / vector**: `sequel` + `sequel_pg` + `pgvector` + `pg`
   - **Ephemeral / hot storage**: `ohm` + `ohm-contrib` + `redis`
   - **Graph / knowledge**: `ruby-wordnet` + `wordnet-defaultdb` (+ `sequel` for persistence; Neo4j via separate driver)
   - **Mixed / polyglot**: all planes — scaffold each layer separately, wire at the end

3. **Confirm embedding backend and dimension** — this is locked at schema creation time, never change it:
   - `informers` with `sentence-transformers/all-MiniLM-L6-v2` → **384 dimensions**
   - `informers` with `nomic-ai/nomic-embed-text-v1` → **768 dimensions** (long-context)
   - `ruby_llm` / OpenAI-compatible → **1536 dimensions** (`text-embedding-3-small`)
   - The `vector(N)` column size in the migration must match the model output exactly — mismatch causes silent insert failures

4. **Confirm async context**: pipeline running inside an `Async` block?
   If yes → non-blocking Sequel dataset operations required.

5. **Confirm circuit breaker requirement**: applies to all external embedding/LLM API calls
   in Standard Mode. Local `informers` inference does NOT require circuit breaker.

---

## Step 2: Detect Mode

**Schema design** — triggered by: design a schema, create a migration, add a column, index strategy, DDL.
Output: Sequel migration file(s) + `dry-schema` contract + index rationale.

**Pipeline scaffolding** — triggered by: build a pipeline, implement chunking, create an ingestion, scaffold a retriever.
Output: single focused Zeitwerk-compliant Ruby file with complete implementation.

**Advisory** — triggered by: how should I model, what's the best way, explain, compare, tradeoffs.
Output: decision table (Reasoning column first, then Decision) + minimal annotated snippet.

**Compound prompts**: split the request, handle the data layer here, state explicitly what should be addressed with `genai` or `tui`.

---

## Step 3: Canonical SFL Schema

### Extension Bootstrap (always first in any SFL migration)

```ruby
run 'CREATE EXTENSION IF NOT EXISTS vector;'
run 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'   # fuzzy lemma matching
run 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
```

### documents — Register Variables (Context stratum)

```ruby
create_table(:documents) do
  primary_key :id, type: :uuid, default: Sequel.function(:uuid_generate_v4)
  String  :title,         text: true, null: false
  String  :corpus_source
  # Register metadata: Field (social activity), Tenor (participant relationships), Mode (language's role)
  # Schema: { "field": "science", "tenor": "expert-to-novice", "mode": "written" }
  column  :register_metadata, :jsonb, default: '{}'
  DateTime :created_at, default: Sequel::CURRENT_TIMESTAMP
  index :register_metadata, type: :gin
end
```

### sentences — Orthographic Structure

```ruby
create_table(:sentences) do
  primary_key :id, type: :uuid, default: Sequel.function(:uuid_generate_v4)
  foreign_key :document_id, :documents, type: :uuid, on_delete: :cascade
  Integer :sequence_index
  Text    :raw_text, null: false
  String  :content_hash, null: false, unique: true  # SHA256 idempotency key
  DateTime :created_at, default: Sequel::CURRENT_TIMESTAMP
end
```

### clauses — Ideational Zone (primary meaning unit)

```ruby
create_table(:clauses) do
  primary_key :id, type: :uuid, default: Sequel.function(:uuid_generate_v4)
  foreign_key :sentence_id, :sentences, type: :uuid, on_delete: :cascade
  # Self-referencing adjacency list for Clause Complex (Taxis: parataxis/hypotaxis)
  foreign_key :parent_complex_id, :clauses, type: :uuid, null: true, on_delete: :set_null
  Integer :sequence_index
  Text    :raw_text, null: false
  String  :content_hash, null: false, unique: true  # SHA256 idempotency key

  # Ideational Metafunction — Transitivity
  String  :process_type, null: false
  constraint(:valid_process_type,
    process_type: %w[material mental relational verbal behavioural existential])
  String  :process_lemma     # base form of ROOT verb (from ruby-spacy)
  # Full ideational structure: participants + circumstances
  column  :ideational_structure, :jsonb, default: '{}'

  # Interpersonal Metafunction — Mood
  String  :mood_type
  constraint(:valid_mood_type,
    mood_type: %w[declarative interrogative imperative exclamative minor])
  column  :interpersonal_structure, :jsonb, default: '{}'

  # Textual Metafunction — Theme/Rheme
  String  :theme_type  # 'topical', 'interpersonal', 'textual', 'multiple'
  column  :thematic_structure, :jsonb, default: '{}'

  # Vector embedding — dimension must match chosen backend (see Step 1)
  column  :embedding, :vector, size: 384  # all-MiniLM-L6-v2 default

  DateTime :created_at, default: Sequel::CURRENT_TIMESTAMP

  # HNSW for ANN semantic search (superior recall vs IVFFlat for large datasets)
  # IVFFlat: faster build, lower recall; HNSW: multi-layer graph, sub-ms retrieval
  index :embedding, name: :clauses_embedding_hnsw_idx,
        type: 'hnsw', op_class: 'vector_cosine_ops'
  # GIN for JSONB containment queries (@> operator)
  index :ideational_structure,   type: :gin
  index :interpersonal_structure, type: :gin
  index :thematic_structure,     type: :gin
  index :process_type
  index :mood_type
end
```

### participants — Polymorphic Participant Roles

```ruby
create_table(:participants) do
  primary_key :id, type: :uuid, default: Sequel.function(:uuid_generate_v4)
  foreign_key :clause_id, :clauses, type: :uuid, on_delete: :cascade
  # Role is determined by process_type + dependency label (nsubj, dobj, iobj)
  String  :role, null: false
  constraint(:valid_role,
    role: %w[actor goal beneficiary senser phenomenon sayer verbiage receiver
             carrier attribute token value behaver existent])
  Text    :entity_text
  String  :ner_label   # spaCy NER: ORG, PERSON, GPE, etc.
  String  :dep_label   # syntactic dep: nsubj, dobj, iobj
  # Per-participant embedding for entity-centric vector search
  column  :embedding, :vector, size: 384
  index :embedding, name: :participants_embedding_hnsw_idx,
        type: 'hnsw', op_class: 'vector_cosine_ops'
  index :role
end
```

---

## Step 4: WordNet → SFL Process Type Mapping

Use `ruby-wordnet` to resolve ROOT verb → lexicographer file → SFL process type.
This is the bridge between syntactic parsing (`ruby-spacy`) and semantic classification (SFL).

```ruby
WORDNET_TO_SFL_PROCESS = {
  'verb.motion'        => 'material',
  'verb.contact'       => 'material',
  'verb.creation'      => 'material',
  'verb.change'        => 'material',
  'verb.cognition'     => 'mental',
  'verb.perception'    => 'mental',
  'verb.emotion'       => 'mental',
  'verb.desire'        => 'mental',
  'verb.communication' => 'verbal',
  'verb.stative'       => 'relational'   # only when lemma is 'be', 'have', 'seem'
}.freeze

# Participant role assignment by process_type + dependency label
PARTICIPANT_ROLES = {
  'material' => { 'nsubj' => 'actor',  'dobj' => 'goal',      'iobj' => 'beneficiary' },
  'mental'   => { 'nsubj' => 'senser', 'dobj' => 'phenomenon'                          },
  'verbal'   => { 'nsubj' => 'sayer',  'dobj' => 'verbiage',  'iobj' => 'receiver'    },
  'relational' => { 'nsubj' => 'carrier', 'dobj' => 'attribute'                        }
}.freeze
```

---

## Step 5: Key Pipeline Patterns

### Linguistically-Motivated Chunking (rank scale: Paragraph → Sentence → Clause)

```ruby
# Use pragmatic_segmenter for sentence boundary detection — preserves cohesive ties
# Never use character-count splitting: destroys thematic structure
require 'pragmatic_segmenter'

module Pipeline
  class LinguisticChunker
    def segment(text)
      PragmaticSegmenter::Segmenter.new(text: text).segment
    end

    def idempotency_key(text)
      Digest::SHA256.hexdigest(text)
    end
  end
end
```

### Hybrid Search (cosine similarity + BM25 scoring)

```ruby
# Combines semantic vector search with lexical relevance (ts_rank)
def hybrid_search(query_text, sfl_filters = {})
  embedding = Informers.pipeline('embedding', 'sentence-transformers/all-MiniLM-L6-v2')
                       .call([query_text]).first

  dataset = DB[:clauses]
  dataset = dataset.where(process_type: sfl_filters[:process_type]) if sfl_filters[:process_type]
  dataset = dataset.where(mood_type: sfl_filters[:mood_type])       if sfl_filters[:mood_type]

  dataset
    .select_append(Sequel.lit(
      "(0.8 * (1 - (embedding <=> ?)) + 0.2 * ts_rank(to_tsvector(raw_text), plainto_tsquery(?))) AS score",
      embedding, query_text
    ))
    .order(Sequel.desc(:score))
    .limit(20)
end
```

### Ohm Hot Storage — Linguistic Hierarchy (Paragraph → Sentence → Word)

```ruby
require 'ohm'

# High-speed scratchpad: traverse document structure in microseconds
# before deep persistence to PostgreSQL
class OhmParagraph < Ohm::Model
  attribute :source_path
  set :sentences, :OhmSentence   # unordered collection
end

class OhmSentence < Ohm::Model
  reference :paragraph, :OhmParagraph
  list      :words, :OhmWord       # list preserves token order
  attribute :content_hash          # SHA256 — drives PostgreSQL idempotency check
end

class OhmWord < Ohm::Model
  attribute :lemma
  attribute :pos_tag    # spaCy POS: NOUN, VERB, ADJ, etc.
  attribute :dep_label  # syntactic dependency: nsubj, dobj, ROOT
end
```

### Transactional Outbox (Neo4j dual-write consistency)

When polyglot persistence includes Neo4j for relationship storage, use the Transactional Outbox pattern to prevent data drift:

```ruby
# graph_sync_outbox migration
create_table(:graph_sync_outbox) do
  primary_key :id
  String   :event_type, null: false   # 'CLAUSE_CREATED', 'ENTITY_LINKED'
  column   :payload, :jsonb, null: false
  String   :status, default: 'pending'  # 'pending', 'processed', 'failed'
  DateTime :created_at, default: Sequel::CURRENT_TIMESTAMP
  index :status
end

# Atomic Sequel transaction: write clause + outbox event in one transaction
DB.transaction do
  clause_id = DB[:clauses].insert(clause_attrs)
  DB[:graph_sync_outbox].insert(
    event_type: 'CLAUSE_CREATED',
    payload: { uuid: clause_id, relationships: derived_edges }.to_json
  )
end
# Background worker processes outbox → Neo4j via MERGE (idempotent)
```

### fast-mcp SFL Tool (MCP interface for agents)

```ruby
require 'fast_mcp'
require 'dry-schema'

class SearchSFLTool < FastMcp::Tool
  description "Search clauses by semantic similarity and SFL structural filters."

  arguments do
    required(:query).filled(:string)
    optional(:sfl_filters).hash do
      optional(:process_type).filled(:string,
        included_in?: %w[material mental relational verbal behavioural existential])
      optional(:participant_role).filled(:string,
        included_in?: %w[actor senser sayer carrier])
      optional(:modality).filled(:string, included_in?: %w[high medium low])
      optional(:mood).filled(:string,
        included_in?: %w[declarative interrogative imperative])
    end
  end

  def call(query:, sfl_filters: {})
    hybrid_search(query, sfl_filters)
  end
end
```

---

## Step 6: Anti-Patterns to Reject

| Anti-Pattern | Correct Approach |
|---|---|
| Document-level chunks | Clause-level granularity — SFL primary meaning unit |
| Mixed embedding dims in one table | One `vector(N)` column, N locked at migration time |
| EAV for participant roles | JSONB `ideational_structure` — role varies by process_type |
| Pure vector search without SFL filters | Hybrid: cosine distance + process_type/mood WHERE clause |
| Neo4j write without outbox | Transactional Outbox — prevents data drift on worker crash |
| Paragraph-level `pragmatic_segmenter` | Sentence-level → clause-level via `ruby-spacy` ROOT detection |
| Missing `pg_trgm` extension | Required for fuzzy lemma matching on `process_lemma` column |
| `CREATE` in Neo4j MERGE step | Always `MERGE` — idempotent re-processing after worker crash |

---

## Step 7: Output Format

**Schema design output:**
1. Sequel migration file with annotated comments explaining each column and index choice
2. `dry-schema` contract for each JSONB column
3. Rationale block: why HNSW vs IVFFlat, why clause-level vs document-level, embedding dimension justification

**Pipeline scaffolding output:**
- Single Zeitwerk-compliant file under appropriate namespace
- Complete implementation — no stubs, no `# TODO` comments
- WARNING block if any gem API was not context-verified

**Advisory output:**
- Decision table: Reasoning column first, then Decision column
- Annotated snippet (≤ 30 lines)
- Explicit gem set from `$CLAUDE_PLUGIN_ROOT/references/gem-registry.md`
