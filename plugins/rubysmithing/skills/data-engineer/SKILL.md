---
name: data-engineer
description: Schema-first data infrastructure skill for Ruby AI systems. Activates on any mention of: PostgreSQL schema design, pgvector, HNSW index, chunking pipeline, embedding strategy, neuro-symbolic RAG, SFL schema, knowledge graph, clauses table, tokens table, clause_complexes, vault_chunks, Ohm model, Redis cache, symbolic metadata, ideational metafunction, transitivity, process type, participant role, register metadata, field tenor mode, entity extraction for storage, sequel migration, content hashing, idempotent pipeline, SHA256 deduplication, WordNet graph, formal concept lattice, hybrid search, RRF, Reciprocal Rank Fusion, hybrid retrieval, clause-level embedding, morphology tagging, POS tagging, dependency parsing, ruby-spacy tokens, lemma, pos_tag, tag_, dep_label, is_stop, is_punct, linguistic forms, IdeationalSchema, SFL annotator, ruby_llm-schema, informers reranker, taxis, clause complex, document ingestion, PDF extraction, DOCX parsing, OCR, kreuzberg, extract_file_sync, HierarchyConfig, batch extraction, document ingestor. Distinguishes schema design (DDL + migration), pipeline scaffolding (executable Ruby), and advisory (rationale + annotated snippet) modes. Always runs rubysmithing-context as a prerequisite step before generating any library-specific code. Single focused file output; specs only on explicit request.
---

# Rubysmithing — Data Engineer

Schema-first designer and pipeline builder for AI data infrastructure in the Ruby terminal-native stack.
SFL (Systemic Functional Linguistics) is the architectural contract: every schema decision maps to a metafunction.

## Core Architectural Principle

**Granularity is clause-level, not document-level.** SFL treats the clause as the primary meaning unit. This enables "Semantic-Functional" retrieval: search for meaning (vector similarity) *within* grammatical structure (SFL process_type, mood, theme filters). Never chunk at the paragraph level when building SFL-aware systems.

---

## Step 0: Document Ingestion (kreuzberg)

When the pipeline input is files (PDF, DOCX, XLSX, images), use `kreuzberg` as the entry point before `pragmatic_segmenter`. Kreuzberg is the Ruby-native document extraction layer — it replaces Docling/PyCall entirely.

```ruby
# frozen_string_literal: true
# lib/<name>/pipeline/document_ingestor.rb

require 'kreuzberg'

extraction_config = Kreuzberg::Config::Extraction.new(
  chunking: Kreuzberg::Config::Chunking.new(
    max_characters: 1000,
    overlap: 100,
    respect_sentences: true,
    respect_paragraphs: false,
    chunker_type: 'text',
    prepend_heading_context: false
  ),
  ocr: Kreuzberg::Config::Ocr.new(backend: 'tesseract', language: 'eng'),
  language_detection: true,
  extract_tables: true,
  extract_images: false,
  use_cache: true,
  output_format: 'markdown'
)

# Single file
result = Kreuzberg.extract_file_sync(path, config: extraction_config)
content       = result.content        # full extracted text
mime_type     = result.mime_type
metadata      = result.metadata       # author, title, dates
tables        = result.tables         # Array of extracted tables
languages     = result.detected_languages

# PDF with heading hierarchy (register_metadata field inference)
pdf_config = Kreuzberg::Config::Extraction.new(
  pdf_options: Kreuzberg::PdfConfig.new(
    hierarchy: Kreuzberg::HierarchyConfig.new(enabled: true),
    extract_images: false,
    passwords: []
  ),
  chunking: Kreuzberg::Config::Chunking.new(max_characters: 1000, overlap: 100, respect_sentences: true)
)
pdf_result = Kreuzberg.extract_file_sync(path, config: pdf_config)
# Traverse heading hierarchy to infer register field:
pdf_result.pages.each do |page|
  page.hierarchy.blocks.each { |b| puts "#{b.level}: #{b.text}" }
end

# Batch ingestion
results = Kreuzberg.batch_extract_bytes_sync(
  [File.read(path1), File.read(path2)],
  ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  extraction_config
)
```

**Handoff to linguistic pipeline:** Pass `result.content` → `LinguisticChunker` (pragmatic_segmenter) → `clauses` table.
**Register_metadata field inference**: use heading hierarchy depth/text to infer `field` (topic domain). `tenor` and `mode` from document metadata or user-provided context.

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
  column  :textual_structure, :jsonb, default: '{}'

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
  index :textual_structure,     type: :gin
  index :process_type
  index :mood_type
end
```

### clause_complexes — Taxis and Logico-Semantic Relations

```ruby
# Handles compound/complex sentences via recursive adjacency list
# Taxis: parataxis (equal status) vs hypotaxis (dependent)
# Logico-Semantic: expansion (elaboration/extension/enhancement) or projection (locution/idea)
create_table(:clause_complexes) do
  primary_key :id, type: :uuid, default: Sequel.function(:uuid_generate_v4)
  foreign_key :sentence_id, :sentences, type: :uuid, on_delete: :cascade
  foreign_key :parent_complex_id, :clause_complexes, type: :uuid, null: true, on_delete: :cascade
  String  :taxis, size: 20              # 'parataxis' | 'hypotaxis'
  String  :logico_semantic_type, size: 20  # 'expansion' | 'projection'
  String  :expansion_mode               # 'elaboration' | 'extension' | 'enhancement'
end
```

### tokens — Atomic Lexical Units (ruby-spacy output)

```ruby
# Every token from ruby-spacy's dependency parse
# Drives: process_type heuristics, participant role assignment, morphological filtering
create_table(:tokens) do
  primary_key :id, type: :uuid, default: Sequel.function(:uuid_generate_v4)
  foreign_key :clause_id, :clauses, type: :uuid, on_delete: :cascade
  String   :text,              null: false
  String   :lemma                          # base form: token.lemma from ruby-spacy
  String   :pos_tag                        # coarse POS: NOUN, VERB, ADJ, ADV, PROPN, etc. (token.pos)
  String   :tag_                           # fine-grained POS: NN, VBD, JJ, etc. (token.tag_)
  String   :dependency_label               # syntactic dep: ROOT, nsubj, dobj, iobj, amod (token.dep)
  Boolean  :is_stop,  default: false       # token.is_stop — stopword flag
  Boolean  :is_punct, default: false       # token.is_punct — punctuation flag
  Integer  :index_in_clause

  # Morphological forms (linguistics gem, keyed by coarse POS)
  # NOUN: plural_form, singular_form
  # VERB: past_tense, present_tense, present_participle, past_participle
  column   :morphological_forms, :jsonb, default: '{}'

  # GIN+trgm on lemma for fuzzy verb/noun matching
  index :lemma, type: :gin, op_class: :gin_trgm_ops
  index :pos_tag
  index :dependency_label
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

## Step 4: ruby-spacy Token Extraction → Tokens Table

```ruby
# Load spaCy model — 'en_core_web_sm' for speed, 'en_core_web_trf' for accuracy
@nlp = Spacy::load('en_core_web_sm')

def extract_tokens(clause_id, text)
  spacy_doc = @nlp.parse(text)

  spacy_doc.each_token.with_index do |token, idx|
    morpho = extract_morphological_forms(token.text, token.pos)

    DB[:tokens].insert(
      clause_id:          clause_id,
      text:               token.text,
      lemma:              token.lemma,
      pos_tag:            token.pos,      # coarse: NOUN, VERB, ADJ
      tag_:               token.tag_,     # fine-grained: NN, VBD, NNS
      dependency_label:   token.dep,      # nsubj, dobj, ROOT, amod
      is_stop:            token.is_stop,
      is_punct:           token.is_punct,
      index_in_clause:    idx,
      morphological_forms: morpho.to_json
    )
  end
end

# ROOT verb detection — entry point for WordNet process classification
def find_root_verb(text)
  @nlp.parse(text).each_token.find { |t| t.dep == 'ROOT' && t.pos == 'VERB' }
end

# Clause boundary heuristics from dependency parse
# Clause-level splits: ROOT, advcl (adverbial clause), ccomp (clausal complement)
CLAUSE_BOUNDARY_DEPS = %w[ROOT advcl ccomp xcomp relcl].freeze
```

### Morphological Forms (linguistics gem, keyed by coarse POS)

```ruby
# Store morphological forms per token JSONB — allows query by tense, number, etc.
def extract_morphological_forms(word, pos_tag)
  forms = {}
  case pos_tag.upcase
  when 'NOUN', 'PROPN'
    forms[:plural_form]    = word.en.plural    rescue nil
    forms[:singular_form]  = word.en.singular  rescue nil
  when 'VERB'
    forms[:past_tense]          = word.en.past_tense           rescue nil
    forms[:present_tense]       = word.en.present_tense        rescue nil
    forms[:present_participle]  = word.en.present_participle   rescue nil
    forms[:past_participle]     = word.en.past_participle      rescue nil
  when 'ADJ'
    forms[:plural_form]  = word.en.plural_adjective  rescue nil
  end
  forms.compact
end
```

---

## Step 5: WordNet → SFL Process Type Mapping

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

## Step 6: Key Pipeline Patterns

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

### Hybrid Search — Reciprocal Rank Fusion (RRF)

RRF is the canonical pattern. It fuses semantic (vector) and structural (SFL SQL) rankings without requiring score normalization. This is superior to weighted average fusion because vector cosine scores and SQL rank scores exist on incompatible scales.

```ruby
# Reciprocal Rank Fusion: combines semantic vector ranking with SFL structural ranking
# Use case: "Find clauses where Government (Actor) acts aggressively on the economy"
def hybrid_search_rrf(query_text, sfl_filters = {})
  query_vec = @embedder.([query_text]).first

  # Semantic ranking: order by cosine distance
  semantic = DB[:clauses]
    .select(:id, Sequel.lit("RANK() OVER (ORDER BY embedding <=> ?)", query_vec.to_s).as(:sem_rank))
    .limit(100)

  # Structural ranking: filter by SFL columns, order by recency as proxy
  structural = DB[:clauses]
  structural = structural.where(process_type: sfl_filters[:process_type]) if sfl_filters[:process_type]
  structural = structural.where(mood_type: sfl_filters[:mood_type]) if sfl_filters[:mood_type]
  if sfl_filters[:participant]
    structural = structural.where(
      Sequel.lit("ideational_structure @> ?", { participants: [sfl_filters[:participant]] }.to_json)
    )
  end
  structural = structural
    .select(:id, Sequel.lit("RANK() OVER (ORDER BY created_at DESC)").as(:str_rank))
    .limit(100)

  # RRF fusion (k=60 is standard constant)
  DB.from(semantic.as(:s))
    .full_outer_join(structural.as(:k), Sequel[:s][:id] => Sequel[:k][:id])
    .select(
      Sequel.function(:coalesce, Sequel[:s][:id], Sequel[:k][:id]).as(:id),
      Sequel.lit("(1.0 / (60 + COALESCE(s.sem_rank, 100))) + (1.0 / (60 + COALESCE(k.str_rank, 100))) AS rrf_score")
    )
    .order(Sequel.desc(:rrf_score))
    .limit(20)
    .all
end

# Tenor analysis: find high-obligation commands
def find_high_modality_commands
  DB[:clauses]
    .where(mood_type: 'imperative')
    .where(Sequel.lit("interpersonal_structure ->> 'modality' = 'high'"))
    .select(:text_content).all
end

# Textual progression: find marked themes (Theme ≠ Subject → discourse framework shift)
def find_marked_themes
  DB[:clauses]
    .where(theme_type: 'topical')
    .exclude(Sequel.lit("textual_structure ->> 'theme' = interpersonal_structure ->> 'subject'"))
    .all
end
```

### Informers Reranker (cross-encoder precision layer)

```ruby
# Three Informers pipeline modes:
@embedder  = Informers.pipeline('embedding', 'sentence-transformers/all-MiniLM-L6-v2')  # 384-dim
@reranker  = Informers.pipeline('reranking', 'mixedbread-ai/mxbai-rerank-base-v1')       # cross-encoder
# @classifier = Informers.pipeline('text-classification', model)                          # optional

# Rerank RRF results with cross-encoder for final precision
def rerank(query, results)
  docs = results.map { |r| r[:text_content] }
  reranked = @reranker.(query, docs)
  reranked.map { |r| results[r[:index]].merge(rerank_score: r[:score]) }
          .sort_by { |r| -r[:rerank_score] }
end
```

### SFL Annotator (ruby_llm-schema + IdeationalSchema)

The neuro-symbolic annotation core: `ruby_llm-schema` constrains LLM output to the JSONB structure of the `ideational_structure` column. This bridges the neural LLM (stochastic annotator) with the symbolic database schema.

```ruby
require 'ruby_llm'
require 'ruby_llm/schema'

class IdeationalSchema < RubyLLM::Schema
  description "SFL Ideational Analysis: Process, Participants, and Circumstances"

  string :process_type,
         enum: %w[material mental relational verbal behavioural existential],
         description: "Category of the process based on Halliday's SFL."

  array :participants, description: "Entities directly involved." do
    object do
      string :role, description: "SFL Role: Actor, Goal, Senser, Phenomenon, Carrier, Attribute, Sayer."
      string :text, description: "Text realizing this participant."
      array  :token_indices, of: :integer
    end
  end

  array :circumstances do
    object do
      string :type, description: "Time, Place, Manner, Cause, Accompaniment, Matter, Role."
      string :text
    end
  end
end

class SFLAnnotator
  def initialize(model: 'claude-sonnet-4-5')
    @chat = RubyLLM.chat(model: model)
  end

  def analyze_clause(clause_text, dependency_hints)
    prompt = <<~TEXT
      Analyze using Systemic Functional Linguistics.
      Clause: "#{clause_text}"
      Syntactic Hints: #{dependency_hints}
      Identify Process Type, Participants, Circumstances.
      Ensure Participant roles match Process Type.
    TEXT
    @chat.with_schema(IdeationalSchema).ask(prompt).content
  end
end
```

### Ohm Hot Storage — Linguistic Hierarchy (Document → Paragraph → Sentence → Token)

```ruby
require 'ohm'
require 'ohm/contrib'

# High-speed scratchpad: traverse document structure in microseconds
# before deep persistence to PostgreSQL. Mirrors the canonical PostgreSQL schema.
class OhmDocument < Ohm::Model
  include Ohm::Contrib::Timestamps
  attribute :title
  attribute :source_path
  attribute :embedding_model   # track which model was used
  set :paragraphs, :OhmParagraph
end

class OhmParagraph < Ohm::Model
  include Ohm::Contrib::Timestamps
  reference :document, :OhmDocument
  attribute :content
  attribute :position
  attribute :embedding          # JSON array — paragraph-level embedding
  set :sentences, :OhmSentence
end

class OhmSentence < Ohm::Model
  include Ohm::Contrib::Timestamps
  reference :paragraph, :OhmParagraph
  attribute :content
  attribute :position
  attribute :content_hash       # SHA256 — gates PostgreSQL clause insert (idempotency)
  attribute :embedding          # JSON array — sentence-level embedding
  list :tokens, :OhmToken       # list preserves token order
  set  :linkages, :OhmLinkage   # optional: LinkParser structural parses
end

class OhmToken < Ohm::Model
  include Ohm::Contrib::Timestamps
  reference :sentence, :OhmSentence
  attribute :text
  attribute :lemma
  attribute :pos          # coarse POS: NOUN, VERB, ADJ (token.pos)
  attribute :tag_         # fine-grained POS: NN, VBD, JJ (token.tag_)
  attribute :dep          # dependency label: nsubj, dobj, ROOT (token.dep)
  attribute :is_stop      # '1' | '0'
  attribute :is_punct     # '1' | '0'
  attribute :position

  # Morphological forms from linguistics gem (stored as JSON string)
  # NOUN: { plural_form:, singular_form: }
  # VERB: { past_tense:, present_tense:, present_participle:, past_participle: }
  attribute :morphological_forms
end

class OhmLinkage < Ohm::Model
  reference :sentence, :OhmSentence
  attribute :diagram        # ASCII diagram from LinkParser
  attribute :linkage_data
  attribute :num_linkages
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

## Step 7: Anti-Patterns to Reject

| Anti-Pattern | Correct Approach |
|---|---|
| Document-level chunks | Clause-level granularity — SFL primary meaning unit |
| Using `thematic_structure` column name | Correct name is `textual_structure` — Theme belongs to Textual metafunction |
| Mixed embedding dims in one table | One `vector(N)` column, N locked at migration time |
| EAV for participant roles | JSONB `ideational_structure` — role varies by process_type |
| Weighted average fusion for hybrid search | RRF (Reciprocal Rank Fusion) — fuses incompatible score scales correctly |
| Pure vector search without SFL filters | Hybrid RRF: vector ranking + SFL structural ranking fused |
| Skipping `tokens` table | `tokens` table is required — drives WordNet classification, morphological queries |
| Skipping `clause_complexes` table | Required for taxis + logico-semantic relations (compound/complex sentences) |
| Neo4j write without outbox | Transactional Outbox — prevents data drift on worker crash |
| Paragraph-level chunking | Sentence → clause boundary via `ruby-spacy` ROOT/advcl/ccomp dep detection |
| Missing `pg_trgm` extension | Required for `gin_trgm_ops` index on `tokens.lemma` for fuzzy matching |
| `CREATE` in Neo4j MERGE step | Always `MERGE` — idempotent re-processing after worker crash |
| LLM output without schema constraint | Use `ruby_llm-schema` + `IdeationalSchema` — constrains LLM to JSONB structure |
| Skipping Informers reranker | Add cross-encoder reranking after RRF for final precision |

---

## Step 8: Output Format

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
