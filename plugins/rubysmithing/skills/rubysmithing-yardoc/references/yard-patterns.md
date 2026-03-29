# YARD Documentation Patterns and Conventions

## Contents
- [Core YARD Tag Reference](#core-yard-tag-reference)
- [Type System Conventions](#type-system-conventions)
- [Documentation Quality Standards](#documentation-quality-standards)
- [Common Anti-Patterns to Avoid](#common-anti-patterns-to-avoid)
- [Project-Specific Customization](#project-specific-customization)
- [YARD Configuration Integration](#yard-configuration-integration)

## Core YARD Tag Reference

### @param Tag Patterns

**Basic Parameter Documentation**
```ruby
# @param [String] name The user's full name
# @param [Integer] age Age in years (must be positive)
# @param [Hash] options Configuration options
```

**Complex Type Specifications**
```ruby
# @param [String, Symbol] identifier Unique identifier (string or symbol)
# @param [Array<String>] tags List of tag names
# @param [Hash{Symbol => Object}] config Configuration hash with symbol keys
# @param [Hash{String => Array<Integer>}] data Nested structure mapping
# @param [#to_s] value Any object that responds to to_s
# @param [#each] collection Enumerable collection
```

**Optional and Default Parameters**
```ruby
# @param [String, nil] description Optional description (default: nil)
# @param [Integer] timeout Timeout in seconds (default: 30)
# @param [Boolean] force Whether to force the operation (default: false)
```

**Block Parameters**
```ruby
# @param [Proc, nil] block Optional block for custom processing
# @yield [String] filename Yields each filename to the block
# @yieldparam [Hash] result Processing result hash
# @yieldreturn [Boolean] true to continue, false to stop
```

### @return Tag Patterns

**Simple Return Types**
```ruby
# @return [String] Formatted name string
# @return [Integer] Number of items processed
# @return [Boolean] true if successful, false otherwise
```

**Conditional Returns**
```ruby
# @return [User, nil] User object if found, nil otherwise
# @return [String] Success message on completion
# @return [Array<Hash>] Array of result hashes, empty if no results
```

**Complex Return Structures**
```ruby
# @return [Hash{Symbol => Object}] Status hash with :success, :message, :data keys
# @return [Enumerator<String>] Enumerator yielding filenames if no block given
# @return [Array<Hash{String => Integer}>] Array of mapping hashes
```

### @raise Tag Patterns

**Exception Documentation**
```ruby
# @raise [ArgumentError] if name is empty or nil
# @raise [TypeError] if options is not a Hash
# @raise [StandardError] if the operation fails due to external factors
# @raise [Errno::ENOENT] if the specified file does not exist
```

**Multiple Exception Scenarios**
```ruby
# @raise [ArgumentError] if required parameters are missing
# @raise [SecurityError] if access is denied
# @raise [TimeoutError] if operation exceeds timeout limit
```

### @example Tag Patterns

**Basic Usage Examples**
```ruby
# @example Basic usage
#   result = process_data("input.txt")
#   result[:status] # => "success"
#
# @example With custom options
#   process_data("data.csv", format: :csv, headers: true)
#   # => {status: "success", rows: 150, headers: ["name", "email"]}
```

**Block Usage Examples**
```ruby
# @example Processing with a block
#   parse_file("data.txt") do |line|
#     puts "Processing: #{line}"
#     line.upcase
#   end
#   # => ["LINE 1", "LINE 2", "LINE 3"]
#
# @example Error handling in blocks
#   safe_process do |item|
#     risky_operation(item)
#   rescue ProcessingError => e
#     log_error(e)
#     nil
#   end
```

**Advanced Scenario Examples**
```ruby
# @example Chaining operations
#   DataProcessor.new
#     .load_from("input.csv")
#     .filter { |row| row[:active] }
#     .transform(:email, &:downcase)
#     .save_to("output.csv")
#   # => 247 # number of processed records
```

## Type System Conventions

### Ruby Core Types
```ruby
String      # Basic string
Symbol      # Symbol literal
Integer     # Numeric integer
Float       # Floating point number
Numeric     # Integer or Float
Boolean     # true or false (YARD convention)
Object      # Any object
NilClass    # Explicitly nil (rarely needed, prefer Type, nil)
```

### Container Types
```ruby
Array               # Array of mixed types
Array<String>       # Array of strings only
Hash                # Hash with mixed key/value types
Hash{String => Object}  # Hash with string keys, any values
Hash{Symbol => String}  # Hash with symbol keys, string values
Range               # Range object
Set<Symbol>         # Set containing symbols
```

### Duck Typing Conventions
```ruby
#to_s        # Object that responds to to_s
#each        # Object that responds to each (Enumerable-like)
#call        # Object that responds to call (Proc-like)
#[]          # Object that supports bracket access
#push        # Object that supports push method
IO          # IO object or IO-like (StringIO, File, etc.)
```

### Nilable Type Patterns
```ruby
String, nil         # String or nil
Array<String>, nil  # Array of strings or nil
Hash, nil          # Hash or nil (prefer specific hash types)
```

### Union Types
```ruby
String, Symbol      # String or Symbol
Integer, String     # Integer or String (for flexible inputs)
File, IO           # File object or any IO
```

## Documentation Quality Standards

### Method Description Guidelines

**Use Active Voice**
```ruby
# ✅ Good: Processes the input file and returns formatted results
# ❌ Bad: Input file is processed and formatted results are returned
```

**Be Specific About Behavior**
```ruby
# ✅ Good: Validates email format and normalizes to lowercase
# ❌ Bad: Handles email processing
```

**Include Important Constraints**
```ruby
# ✅ Good: Calculates compound interest using daily compounding
# ❌ Bad: Calculates interest
```

### Parameter Description Best Practices

**Describe Purpose and Constraints**
```ruby
# ✅ Good: @param [String] email Valid email address (will be normalized)
# ❌ Bad: @param [String] email The email
```

**Document Expected Format**
```ruby
# @param [String] date_string Date in YYYY-MM-DD format
# @param [Hash] config Configuration with required :host and :port keys
# @param [Array<String>] paths Absolute file paths (must exist)
```

**Clarify Optional Behavior**
```ruby
# @param [String, nil] prefix Optional prefix for output (default: timestamp)
# @param [Boolean] validate Whether to validate input (default: true)
```

### Return Value Documentation Standards

**Describe Structure and Content**
```ruby
# ✅ Good: @return [Hash{Symbol => Object}] Result hash with :data, :errors, :meta keys
# ❌ Bad: @return [Hash] The results
```

**Document Conditional Returns**
```ruby
# @return [Array<User>] Matching users (empty array if none found)
# @return [String, nil] Error message if validation fails, nil if successful
```

### Example Quality Criteria

**Use Realistic Data**
```ruby
# ✅ Good:
# @example
#   user = User.find_by_email("john@example.com")
#   user.full_name # => "John Smith"
#
# ❌ Bad:
# @example
#   user = User.find_by_email("email")
#   user.full_name # => "name"
```

**Show Expected Output**
```ruby
# ✅ Good:
# @example Parsing CSV data
#   parse_csv("name,age\nJohn,30\nJane,25")
#   # => [{name: "John", age: 30}, {name: "Jane", age: 25}]
```

**Include Error Cases When Relevant**
```ruby
# @example Error handling
#   begin
#     process_file("nonexistent.txt")
#   rescue FileNotFoundError => e
#     puts "File missing: #{e.message}"
#   end
```

## Common Anti-Patterns to Avoid

### Vague Descriptions
```ruby
# ❌ Bad: Processes data
# ✅ Good: Converts CSV data to hash objects with symbol keys
```

### Missing Type Information
```ruby
# ❌ Bad: @param data The data to process
# ✅ Good: @param [Array<Hash>] data Array of record hashes
```

### Trivial Examples
```ruby
# ❌ Bad:
# @example
#   add(1, 2) # => 3
#
# ✅ Good:
# @example Calculate total with tax
#   add_tax(100.00, rate: 0.08) # => 108.00
```

### Over-Documentation
```ruby
# ❌ Bad: Document every getter/setter with obvious behavior
# ✅ Good: Document complex methods, leave simple accessors undocumented
```

### Inconsistent Terminology
```ruby
# ❌ Bad: Mix "user", "person", "account" for the same concept
# ✅ Good: Use consistent terminology throughout documentation
```

## Project-Specific Customization

### Detecting Documentation Patterns

**Scan for existing patterns:**
- Consistent use of @since tags indicates version tracking
- Custom tags suggest extended documentation requirements
- Specific type annotation styles should be maintained
- Example verbosity levels should match project standards

**Common project variations:**
- Some projects prefer `Boolean` vs `true, false` for boolean types
- Version numbering schemes for @since tags
- Custom tags for API stability (@api private, @api public)
- Integration with external documentation systems

### Integration Guidelines

**Preserve existing structure:**
- Maintain spacing and indentation patterns
- Keep existing custom tags and annotations
- Respect established parameter ordering in documentation
- Follow existing example formatting conventions

**Handle special cases:**
- Metaprogrammed methods may need manual annotation
- DSL methods often require usage context examples
- Callback methods need lifecycle documentation
- Private methods may follow different documentation standards

## YARD Configuration Integration

### Common .yardopts Patterns
```
--readme README.md
--files CHANGELOG.md,LICENSE
--protected
--private
--exclude spec/
--markup markdown
--output-dir doc/
```

### Custom Tag Support
```ruby
# Common custom tags found in Ruby projects:
# @api private    # Internal API not for public use
# @api stable     # Stable public API
# @deprecated     # Marked for removal
# @experimental   # New feature, may change
# @todo          # Future enhancement needed
```

### Markup and Linking
```ruby
# Cross-references
# @see OtherClass#method
# @see http://example.com/docs

# Inline code formatting
# Use +code+ for inline code references
# Use {ClassName} for class references
# Use {#method_name} for method references in same class
```