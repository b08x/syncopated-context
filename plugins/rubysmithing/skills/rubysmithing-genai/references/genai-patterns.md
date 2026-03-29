# GenAI Patterns

Implementation patterns for the AI/NLP layer. Referenced by rubysmithing-genai
before scaffolding. Always verify current API syntax via rubysmithing-context
before generating — these patterns show structure, not guaranteed current syntax.

## Contents
- [RubyLLM Chat](#rubyllm-chat)
- [RubyLLM Agent & Tool Classes](#rubyllm-agent--tool-classes)
- [RAG Pipeline](#rag-pipeline)
- [DSPy Reasoning Modules](#dspy-reasoning-modules)
- [MCP Server](#mcp-server)
- [Embedding Generator (local vs remote)](#embedding-generator-local-vs-remote)
- [NLP Processor (ruby-spacy)](#nlp-processor-ruby-spacy)
- [Async + Circuit Breaker Wrapper](#async--circuit-breaker-wrapper-apply-to-all-external-calls)

---

## RubyLLM Chat

### Basic Chat
```ruby
# Always query: /crmne/ruby_llm "chat basic usage"
chat = RubyLLM.chat(model: "claude-sonnet-4-5")
response = chat.ask("What is RAG?")
puts response.content
```

### Streaming
```ruby
chat.ask("Explain embeddings") do |chunk|
  print chunk.content
end
```

### Tool Calling
```ruby
# Define tools as Ruby blocks — verify current tool definition syntax via Context7
chat = RubyLLM.chat(model: "claude-sonnet-4-5")
chat.with_tool(:search) do |query:|
  SearchService.call(query)
end
response = chat.ask("Search for recent AI papers")
```

### Structured Output (ruby_llm-schema)
```ruby
# Query: /danielfriis/ruby_llm-schema "schema validation response"
```

---

## RubyLLM Agent & Tool Classes

Class-based patterns for building structured agents and reusable tools.
All syntax verified via Context7 (`/crmne/ruby_llm`).

### Basic Tool Class

```ruby
# frozen_string_literal: true

# A tool is a Ruby class inheriting from RubyLLM::Tool.
# description → what the tool does (shown to the model)
# param → declares an argument with optional type, desc, required
# execute → the method the model calls; must accept keyword args

class Weather < RubyLLM::Tool
  description "Gets current weather for a location"
  param :city, desc: "City name"
  param :units, type: :string, desc: "celsius or fahrenheit", required: false

  def execute(city:, units: "celsius")
    response = Faraday.get("https://api.weather.com/#{city}&units=#{units}")
    JSON.parse(response.body)
  rescue => e
    { error: e.message }
  end
end

# Attach to a chat instance
chat = RubyLLM.chat(model: "gpt-4o")
chat.with_tool(Weather)
response = chat.ask("What's the weather in Tokyo?")
```

### Tool with Typed Parameters

```ruby
class Calculator < RubyLLM::Tool
  description "Performs basic arithmetic"
  param :expression, desc: "Mathematical expression to evaluate"

  def execute(expression:)
    { result: eval(expression) }
  end
end
```

### Tool with Dependencies (initialize)

```ruby
class DocumentSearch < RubyLLM::Tool
  description "Searches documents by relevance"
  param :query, desc: "The search query"
  param :limit, type: :integer, desc: "Maximum number of results", required: false

  def initialize(database)
    @database = database
  end

  def execute(query:, limit: 5)
    @database.search(query, limit: limit)
  end
end

# Pass dependencies at instantiation
search_tool = DocumentSearch.new(MyDatabase)
chat.with_tool(search_tool)
```

### Tool Call Callbacks

```ruby
chat = RubyLLM.chat(model: "gpt-4o")
  .with_tool(Weather)
  .on_tool_call do |tool_call|
    logger.info("Tool invoked", name: tool_call.name, args: tool_call.arguments)
  end
  .on_tool_result do |result|
    logger.info("Tool returned", result: result)
  end

response = chat.ask("What's the weather in Paris?")
```

### Streaming with Tools

```ruby
chat = RubyLLM.chat(model: "gpt-4o").with_tool(Weather)

chat.ask("What's the weather in Berlin?") do |chunk|
  if chunk.tool_calls
    name = chunk.tool_calls.values.first.name
    print "\n[TOOL CALL: #{name}]\n"
  elsif chunk.content
    print chunk.content
  end
end
```

### Basic Agent

```ruby
# frozen_string_literal: true

# An agent is a Ruby class inheriting from RubyLLM::Agent.
# model → which LLM to use
# instructions → system prompt (shown on every turn)
# tools → list of Tool classes available to the agent

class SupportAgent < RubyLLM::Agent
  model "gpt-4o"
  instructions "You are a concise support assistant."
  tools SearchDocs, LookupAccount
end

response = SupportAgent.new.ask("How do I reset my API key?")
```

### Agent with Full Configuration

```ruby
class WorkAssistant < RubyLLM::Agent
  model "claude-sonnet-4-5"
  instructions "You are a helpful assistant. Always cite sources."
  tools SearchDocs, LookupAccount
  temperature 0.2
  params max_output_tokens: 256
end
```

### Agent with Rails Chat Model

```ruby
class WorkAssistant < RubyLLM::Agent
  chat_model Chat  # persisted Chat record (Rails)
  model "claude-sonnet-4-5"
  instructions "You are a helpful assistant."
  tools SearchDocs, LookupAccount
end
```

### Multi-Tool Agent Example

```ruby
# frozen_string_literal: true

# --- Tools ---

class WebSearch < RubyLLM::Tool
  description "Search the web for information"
  param :query, desc: "Search query"

  def execute(query:)
    # Integration with search provider
    { results: SearchService.call(query) }
  end
end

class Calculator < RubyLLM::Tool
  description "Perform arithmetic calculations"
  param :expression, desc: "Math expression"

  def execute(expression:)
    { result: eval(expression) }
  end
end

class FileLookup < RubyLLM::Tool
  description "Look up file contents by path"
  param :path, desc: "File path to read"

  def execute(path:)
    { content: File.read(path) }
  rescue Errno::ENOENT
    { error: "File not found: #{path}" }
  end
end

# --- Agent ---

class ResearchAssistant < RubyLLM::Agent
  model "claude-sonnet-4-5"
  instructions <<~PROMPT
    You are a research assistant with access to web search,
    calculator, and file lookup tools. Always cite your sources.
    Use the most specific tool available for each task.
  PROMPT
  tools WebSearch, Calculator, FileLookup
  temperature 0.3
end

# Usage
assistant = ResearchAssistant.new
response = assistant.ask("Summarize the latest papers on transformer architectures")
puts response.content
```

---

## RAG Pipeline

### Document Ingestion
```ruby
# frozen_string_literal: true
# Query: /jeremyevans/sequel "insert batch" and /pgvector/pgvector "vector column insert"

module MyApp
  module RAG
    class Ingester
      def ingest(document:, source:)
        chunks = segment(document)
        embeddings = embed_batch(chunks)
        store_batch(chunks, embeddings, source:)
      end

      private

      def segment(text)
        PragmaticSegmenter::Segmenter.new(text: text).segment
      end

      def embed_batch(chunks)
        # ruby_llm batch embedding — verify current API via Context7
        chunks.map { |chunk| RubyLLM.embed(chunk) }
      end

      def store_batch(chunks, embeddings, source:)
        DB.transaction do
          chunks.zip(embeddings).each do |chunk, embedding|
            DB[:documents].insert(
              content: chunk,
              embedding: embedding.vector,  # pgvector column
              source: source
            )
          end
        end
      end
    end
  end
end
```

### Query / Retrieval
```ruby
module MyApp
  module RAG
    class Retriever
      K = 5  # top-k results

      def retrieve(query:)
        query_embedding = RubyLLM.embed(query).vector
        DB[:documents]
          .select(:content, :source)
          .order(Sequel.lit("embedding <=> ?", query_embedding))
          .limit(K)
          .all
      end
    end
  end
end
```

### Full RAG Chain
```ruby
module MyApp
  module RAG
    class Pipeline
      def run(query:)
        context = Retriever.new.retrieve(query:)
        augmented_prompt = build_prompt(query:, context:)
        RubyLLM.chat.ask(augmented_prompt)
      end

      private

      def build_prompt(query:, context:)
        chunks = context.map { |r| r[:content] }.join("\n\n")
        "Context:\n#{chunks}\n\nQuestion: #{query}"
      end
    end
  end
end
```

---

## DSPy Reasoning Modules

```ruby
# Query: /vicentereig/dspy.rb "signature predict chain of thought"
# Structure — verify syntax via Context7 before use

module MyApp
  module Reasoning
    # Signature defines input/output contract
    class SummarizeSignature < DSPy::Signature
      input :document, type: :string, desc: "Document to summarize"
      output :summary, type: :string, desc: "Concise summary"
      output :key_points, type: :array, desc: "Bullet points"
    end

    # Module uses the signature
    class Summarizer < DSPy::Module
      def initialize
        @predict = DSPy::ChainOfThought.new(SummarizeSignature)
      end

      def forward(document:)
        @predict.call(document: document)
      end
    end
  end
end
```

---

## MCP Server

```ruby
# Query: /yjacquin/fast-mcp "tool definition server boot"
# Structure — verify syntax via Context7

require "fast_mcp"

server = FastMCP::Server.new("my-mcp-server")

server.tool "search_documents",
  description: "Search the document store by semantic similarity",
  parameters: {
    query: { type: "string", description: "Search query" },
    k:     { type: "integer", description: "Number of results", default: 5 }
  } do |query:, k: 5|
    MyApp::RAG::Retriever.new.retrieve(query:, k:).to_json
  end

server.run
```

---

## Embedding Generator (local vs remote)

### Remote (ruby_llm)
```ruby
module MyApp
  module Embeddings
    class RemoteGenerator
      MODEL = "text-embedding-3-small"

      def generate(text)
        RubyLLM.embed(text, model: MODEL)
      end

      def generate_batch(texts)
        texts.map { |t| generate(t) }
      end
    end
  end
end
```

### Local (informers)
```ruby
# Query: /ankane/informers "embedding model usage"
module MyApp
  module Embeddings
    class LocalGenerator
      def initialize
        # Verify current Informers API via Context7
        @model = Informers.pipeline("feature-extraction", "sentence-transformers/all-MiniLM-L6-v2")
      end

      def generate(text)
        @model.call(text)
      end
    end
  end
end
```

---

## NLP Processor (ruby-spacy)

```ruby
# Query: /yohasebe/ruby-spacy "pipeline entity extraction"
module MyApp
  module NLP
    class Processor
      def initialize
        # Verify current ruby-spacy API via Context7
        @nlp = Spacy::Language.new("en_core_web_sm")
      end

      def extract_entities(text)
        doc = @nlp.read(text)
        doc.ents.map { |ent| { text: ent.text, label: ent.label_ } }
      end

      def segment_sentences(text)
        doc = @nlp.read(text)
        doc.sents.map(&:text)
      end
    end
  end
end
```

---

## Async + Circuit Breaker Wrapper (apply to all external calls)

```ruby
# Wrap any LLM call in both async context and circuit breaker
module MyApp
  module AI
    class ResilientClient
      include BreakerMachines::DSL

      circuit_breaker :llm_api,
        threshold: 5,
        timeout: 30,
        reset_timeout: 60

      def call_async(prompt)
        Async do
          with_circuit_breaker(:llm_api) do
            RubyLLM.chat.ask(prompt)
          end
        end
      end
    end
  end
end
```
