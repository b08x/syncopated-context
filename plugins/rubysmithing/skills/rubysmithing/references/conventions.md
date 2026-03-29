# Ruby Conventions Reference

Fallback conventions when no project config is detected.
Covers community idioms, stack-specific patterns, and Zeitwerk compliance rules.

## Contents
- [File & Module Structure](#file--module-structure)
- [Naming Conventions](#naming-conventions)
- [Method Design](#method-design)
- [Module Patterns](#module-patterns)
- [Value Objects](#value-objects)
- [Error Handling](#error-handling)
- [Configuration Pattern](#configuration-pattern)
- [Logging](#logging)
- [Async Pattern](#async-pattern)
- [Circuit Breaker Pattern](#circuit-breaker-pattern)
- [Parallel Processing Patterns](#parallel-processing-patterns)
- [Data Processing Patterns](#data-processing-patterns)


## File & Module Structure

### Zeitwerk Compliance
File paths must mirror module/class hierarchy exactly:
```
lib/my_app/data/processor.rb  →  MyApp::Data::Processor
lib/my_app/agents/chat.rb     →  MyApp::Agents::Chat
```

Root namespace maps to `lib/[app_name]/`. The loader is configured in the entry point:
```ruby
# app.rb / bin/[name]
loader = Zeitwerk::Loader.for_gem  # for gems
# or
loader = Zeitwerk::Loader.new      # for standalone apps
loader.push_dir("#{__dir__}/lib")
loader.setup
```

### Magic Comment
All files must start with:
```ruby
# frozen_string_literal: true
```

## Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Methods | `snake_case` | `process_document` |
| Variables | `snake_case` | `embedding_vector` |
| Classes | `CamelCase` | `DataProcessor` |
| Modules | `CamelCase` | `EmbeddingHelpers` |
| Constants | `SCREAMING_SNAKE` | `MAX_TOKENS` |
| Predicates | `?` suffix | `ready?`, `streaming?` |
| Mutators | `!` suffix | `save!`, `process!` |
| Private helpers | `_` prefix optional | `_build_payload` |

## Method Design

### Keyword Arguments (3+ params)
```ruby
# Bad
def embed(text, model, batch_size, normalize)

# Good
def embed(text:, model: "text-embedding-3-small", batch_size: 100, normalize: true)
```

### Guard Clauses
```ruby
# Bad
def process(doc)
  if doc
    if doc.valid?
      if doc.content.present?
        # ... actual logic
      end
    end
  end
end

# Good
def process(doc)
  return unless doc
  return unless doc.valid?
  return if doc.content.empty?
  # ... actual logic
end
```

### Method Length
- Soft limit: 15 lines
- Hard limit: 30 lines — extract to private methods

## Module Patterns

### Utility Modules (no instance state)
```ruby
# Bad
module TextUtils
  extend self
  def normalize(text) = text.strip.downcase
end

# Good
module TextUtils
  module_function
  def normalize(text) = text.strip.downcase
end
```

### Mixins (instance behavior)
```ruby
module Embeddable
  def embed
    EmbeddingGenerator.run(content: to_s)
  end
end
```

## Value Objects

Use `Struct.new(keyword_init: true)` for simple data containers:
```ruby
EmbeddingResult = Struct.new(
  :vector,
  :model,
  :token_count,
  keyword_init: true
)
```

## Error Handling

### Custom Error Classes
```ruby
module MyApp
  Error = Class.new(StandardError)
  
  module Agents
    AgentError     = Class.new(MyApp::Error)
    TimeoutError   = Class.new(AgentError)
    ToolCallError  = Class.new(AgentError)
  end
end
```

### Never Silently Rescue
```ruby
# Bad
rescue => e
  nil

# Bad
rescue Exception => e  # catches SystemExit, SignalException

# Good
rescue MyApp::Error => e
  logger.error("Operation failed", error: e.message, class: e.class.name)
  raise  # or handle explicitly
```

## Configuration Pattern

Two-tier config (always):
```ruby
# config/application.rb
# frozen_string_literal: true

require "dotenv/load"       # loads .env into ENV
require "tty-config"

module MyApp
  class Configuration
    def self.load
      config = TTY::Config.new
      config.append_path(Dir.home)
      config.append_path(Dir.pwd)
      config.set_from_env("DATABASE_URL", var: "DATABASE_URL")
      config.set_from_env("LLM_API_KEY",  var: "ANTHROPIC_API_KEY")
      config
    end
  end
end
```

## Logging

Always use structured logging, never puts:
```ruby
require "journald/logger"

module MyApp
  LOGGER = Journald::Logger.new("my_app")

  LOGGER.info("Processing document", doc_id: doc.id, size: doc.size)
  LOGGER.error("API call failed",    error: e.message, attempt: attempt)
end
```

## Async Pattern

```ruby
require "async"

# Fiber-based I/O concurrency
Async do |task|
  task.async { fetch_document(url_1) }
  task.async { fetch_document(url_2) }
end

# With barrier (wait for all)
Async do
  barrier = Async::Barrier.new
  urls.each { |url| barrier.async { fetch(url) } }
  barrier.wait
end
```

## Circuit Breaker Pattern

All external API calls must be wrapped:
```ruby
require "circuit_breaker"

class LLMClient
  include CircuitBreaker

  def complete(prompt)
    ruby_llm_call(prompt)
  end

  circuit_method :complete

  circuit_handler do |handler|
    handler.failure_threshold = 5
    handler.failure_timeout = 60
    handler.invocation_timeout = 30
    handler.logger = LOGGER
  end
end
```

## Parallel Processing Patterns

### CPU-bound work distribution

```ruby
require "parallel"

# Process items across multiple processes
results = Parallel.map(items, in_processes: 4) do |item|
  # CPU-intensive work
  item.heavy_computation
end

# With progress tracking
results = Parallel.map_with_index(items, in_processes: 4) do |item, index|
  LOGGER.info("Processing", index: index, total: items.size)
  item.process
end
```

### Concurrent primitives for shared state

```ruby
require "concurrent-ruby"

# Thread-safe counter
counter = Concurrent::AtomicFixnum.new(0)

# Future-based async computation
future = Concurrent::Future.execute { expensive_operation }
result = future.value  # blocks until complete

# Thread pool for I/O bound work (complement to Async fibers)
pool = Concurrent::ThreadPoolExecutor.new(min_threads: 2, max_threads: 10)
promise = Concurrent::Promise.execute(executor: pool) { api_call }
```

## Data Processing Patterns

### JSON streaming for large files

```ruby
require "yajl-ruby"

# Stream parse large JSON files
parser = Yajl::Parser.new
parser.on_parse_complete = ->(obj) { process_object(obj) }

File.open("large_file.json") do |file|
  parser << file.read(8192) while !file.eof?
end
```

### Markdown processing

```ruby
require "commonmarker"
require "kramdown"

# Fast C-backed parser for deterministic output
def parse_markdown_fast(text)
  CommonMarker.render_html(text, :DEFAULT, [:table, :strikethrough])
end

# Pure Ruby parser when extensibility needed
def parse_markdown_extensible(text)
  Kramdown::Document.new(text).to_html
end
```

### Content sanitization

```ruby
require "loofah"

def sanitize_html(content)
  # Remove scripts, normalize structure
  Loofah.fragment(content).scrub!(:escape)
end

def extract_text(html)
  # Strip all HTML tags, keep text content
  Loofah.fragment(html).text
end
```
