---
name: genai
description: AI/NLP component scaffolder and advisor for Ruby projects. Activates on any mention of: LLM chat, chatbot, agent, tool-calling, function calling, RubyLLM::Agent, RubyLLM::Tool, streaming, RAG, retrieval augmented generation, vector search, semantic search, embedding, pgvector, DSPy, reasoning module, chain of thought, ReAct, MCP server, MCP tool, model context protocol, ruby_llm, RubyLLM, NLP, entity extraction, named entity recognition, sentence segmentation, chunking, document processing, local inference, informers, spaCy, ruby-spacy, prompt pipeline, or structured output. Detects whether request is scaffolding (generate file) or advisory (explain approach). Always runs rubysmithing-context as a prerequisite step before generating any library-specific code. Single focused file output; specs only on explicit request.
---

# Rubysmithing — GenAI

Scaffolder and advisor for AI/NLP components in the Ruby terminal-native stack.
Generates single focused implementation files or explains integration patterns.

## Step 1: Prerequisites (Always Run First)

Before generating any implementation code:

1. **Activate rubysmithing-context** for every gem involved in this task.
   This is not optional — generate no library-specific code until API syntax is confirmed
   or a `[WARNING: Unverified API Syntax]` block has been injected.

2. **Identify architectural plane**: reasoning, retrieval, NLP, neuro-symbolic, or transport?

3. **Confirm async context**: will this run inside an `Async` block?
   If yes → non-blocking patterns required.

4. **Confirm circuit breaker requirement**: applies to all external LLM API calls
   in Standard Mode. Omit in Lite Mode (task ≤ ~50 lines).

## Step 2: Detect Mode

**Scaffolding** — triggered by: create, build, implement, generate, scaffold, write me a.
Output: single focused file, Zeitwerk-compliant path, complete implementation.

**Advisory** — triggered by: how do I, explain, what's the best way, compare, should I use.
Output: recommendation + minimal snippet. No full file unless asked.

**Compound prompts** (e.g., "refactor this RAG pipeline AND build a TUI for it"):
Split the request. Handle the GenAI component here. State explicitly:
"Handling the RAG pipeline component. The TUI dashboard component should be
addressed with tui."

## Architectural Plane Reference

| Plane | Gems | Scope |
|---|---|---|
| **reasoning** | `ruby_llm`, `dspy.rb`, `ruby_llm-schema` | LLM agents, tool calling, structured output, SFL annotation |
| **retrieval** | `ruby_llm`, `informers`, `pgvector`, `sequel` | Embedding generation, RAG, RRF hybrid search, reranking |
| **NLP** | `ruby-spacy`, `pragmatic_segmenter`, `ruby-wordnet`, `lingua` | Token extraction, POS/dep/NER, morphology, process classification |
| **neuro-symbolic** | `ruby-spacy` + `ruby_llm-schema` + `sequel` + `pgvector` | SFL annotation pipeline: symbolic parse → LLM schema-constrained annotation → clause-level storage |
| **transport** | `fast-mcp`, `async`, `circuit_breaker` | MCP servers, async concurrency, resilience |

**Neuro-symbolic plane**: The combination of symbolic NLP (`ruby-spacy` dependency parse → `ruby-wordnet` process classification) with neural annotation (`ruby_llm` + `ruby_llm-schema` `IdeationalSchema`) and neural retrieval (`informers` embeddings + `pgvector` RRF). Always delegate schema/storage concerns to `agentic-data-engineer`. Handle only the LLM annotation and agent orchestration layers here.

**ruby_llm-schema SFL annotation pattern** (neuro-symbolic core):
```ruby
class IdeationalSchema < RubyLLM::Schema
  string :process_type, enum: %w[material mental relational verbal behavioural existential]
  array  :participants do
    object do
      string :role   # Actor, Goal, Senser, Phenomenon, Carrier, Attribute, Sayer
      string :text
      array  :token_indices, of: :integer
    end
  end
  array :circumstances do
    object { string :type; string :text }
  end
end
# Usage: @chat.with_schema(IdeationalSchema).ask(clause_prompt).content
```

**Compound prompts involving schema/storage**: Split the request. State explicitly:
"Handling the LLM annotation/agent component. The schema/pipeline component should be addressed with `agentic-data-engineer`."

## Patterns Reference

Load `$CLAUDE_PLUGIN_ROOT/references/genai-patterns.md` for implementation patterns:
RubyLLM::Agent configuration, RubyLLM::Tool class definitions, chatbot,
RAG ingestion/retrieval/full pipeline, DSPy modules, MCP server,
embedding generator (remote vs local), NLP processor, async+circuit breaker wrapper.

## Scaffolding Output Format

1. **File path** — single focused file, Zeitwerk-compliant
2. **Complete implementation** — no stubs, no placeholder comments
3. **Required gems** — Gemfile additions
4. **Context7 IDs used** — which gem docs were resolved (or WARNING if unresolved)
5. **Integration note** — how this file connects to the broader stack

## Advisory Output Format

1. **Recommendation** — direct answer, no hedging
2. **Minimal code snippet** — not a full file
3. **Trade-offs** — if multiple approaches exist, name them with one-line trade-offs

## Specs

Generate RSpec specs only when explicitly requested:

- Stub external LLM calls with VCR or manual doubles
- Test reasoning logic, not API response content
- File: `spec/[path_matching_lib_file]_spec.rb`
