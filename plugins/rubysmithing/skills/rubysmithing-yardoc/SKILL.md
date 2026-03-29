---
name: rubysmithing-yardoc
description: YARD documentation generator with semantic analysis for Ruby files. Automatically activates on requests to generate, add, or improve YARD documentation. Uses AST parsing and type inference to generate comprehensive @param, @return, @example, and @raise tags. Maintains consistency with existing project documentation patterns and YARD configuration. Generates production-grade documentation that eliminates usage pitfalls and accelerates correct method implementation. Requires rubysmithing-context when the target file uses non-stdlib gems, to ensure type annotations reflect verified API shapes.
---

# Rubysmithing — YARD Documentation Generator

Semantic analysis-powered YARD documentation generator. Transforms Ruby code into comprehensive, immediately usable developer resources with precise implementation guidance.

## When This Skill Activates

Activate on any mention of:

- "generate YARD documentation", "add YARD comments", "document this code"
- "yardoc", "yard", "@param", "@return", "@example"
- "document methods", "generate docs", "add documentation"
- File paths ending in `.rb` + documentation request
- "improve documentation", "better docs", "missing documentation"

Skip activation for: README generation, project overview docs, non-Ruby files.

## Step 0: Gem Context Check (Prerequisite)

Before generating type annotations, check whether the target file uses non-stdlib gems.

If gem-specific types appear in method signatures or return values (e.g., `RubyLLM::Chat`,
`Sequel::Dataset`, `Async::Task`, `Dry::Schema::Result`):

1. **Activate rubysmithing-context** for each gem involved.
   Type annotations derived from unverified API shapes produce misleading documentation.
2. Use verified method signatures verbatim in `@param` and `@return` tags.
3. If Context7 is unavailable, apply the tiered fallback from `rubysmithing-context`
   and note `# type annotation based on stale cache — verify before publishing` inline.

Skip this step for: stdlib-only files, Lite Mode tasks, gems already resolved this session.

---

## Step 1: Validate Target and Context

### Target File Validation

- Verify specified Ruby file exists and is readable
- Confirm `.rb` extension (warn if missing but proceed)
- Parse file for basic syntax validity before analysis

### Documentation Context Assessment

- Check for `.yardopts` file to maintain project YARD configuration
- Scan existing codebase for established documentation patterns
- Identify documentation coverage gaps and consistency issues
- Note any existing YARD comment style conventions

## Step 2: Semantic Code Analysis

### AST-Based Structure Parsing

Use Ruby parser to extract:

- Class and module hierarchies with inheritance chains
- Method signatures including parameter types and defaults
- Instance vs class method distinction
- Public, private, protected method visibility
- Block parameter usage patterns and yields

### Type Inference Engine

Analyze code implementation to infer:

- Parameter types from usage patterns and method calls
- Return value types from conditional branches and explicit returns
- Nilable returns from conditional logic and early returns
- Duck typing interfaces from method calls on parameters
- Exception conditions from raise statements and rescue blocks

### Behavioral Pattern Recognition

Extract method purpose from:

- Implementation logic and control flow
- Parameter interactions and transformation patterns
- Side effects and state mutations
- Integration with other methods and external dependencies

## Step 3: YARD Documentation Generation

### Method Documentation Assembly

Generate complete YARD comment blocks with:

```ruby
##
# [Clear behavioral description in active voice]
#
# [Extended description with usage context and important notes]
#
# @param [PreciseType] param_name Description with usage context and constraints
# @param [Type, nil] optional_param Description including default behavior patterns
# @return [SpecificType] Comprehensive description with type structure details
# @raise [ExceptionClass] Specific conditions that trigger this exception
# @example Basic usage pattern
#   realistic_method_call(actual_values)
#   # => expected_output_with_type
# @example Advanced scenario with blocks
#   complex_usage_pattern do |yielded_value|
#     # practical block implementation
#   end
# @since version_number (if determinable from git history)
# @see RelatedClass#related_method (if cross-references detected)
```

### Type Annotation Precision

- Use specific Ruby types: `String`, `Integer`, `Hash{Symbol => Object}`
- Document complex structures: `Array<Hash{String => Symbol}>`
- Include duck typing: `#to_s`, `#each`, `#call`
- Specify nilable types: `String, nil` for conditional returns
- Document union types: `String, Symbol` for flexible parameters

### Example Generation Strategy

Create realistic, working code examples:

- Use actual parameter values that demonstrate typical usage
- Show return value structure with comments
- Include both simple and complex usage scenarios
- Demonstrate block usage patterns where applicable
- Avoid trivial examples that don't add value

## Step 4: Documentation Quality Assurance

### Validation Checklist

- **Type Accuracy**: Verify type annotations match actual code behavior
- **Example Validation**: Ensure all examples are syntactically correct and realistic
- **Completeness**: Check all method parameters and return scenarios are documented
- **Consistency**: Maintain terminological and structural consistency across methods
- **YARD Compliance**: Validate generated syntax against YARD standards

### Integration Verification

- Preserve existing comment structure and formatting
- Maintain project-specific documentation conventions
- Ensure generated documentation integrates cleanly with existing docs
- Verify no conflicts with existing YARD tags or custom extensions

## Step 5: Output and Application

### Documentation Insertion

- Insert generated YARD comments at appropriate code locations
- Preserve existing code structure and indentation
- Maintain proper spacing between methods and comment blocks
- Handle edge cases like nested classes and metaprogramming

### Quality Report Summary

Provide completion summary:

- Number of methods documented
- Types of documentation generated (params, returns, examples, etc.)
- Any limitations or unresolved patterns encountered
- Suggestions for manual review or enhancement

## Advanced Features

### Project Pattern Learning

- Detect and follow established parameter naming conventions
- Match existing documentation verbosity and style preferences
- Inherit project-specific type annotation patterns
- Respect existing @since, @deprecated, and custom tag usage

### Error Handling Protocol

- If file parsing fails: Report specific syntax issues and suggest fixes
- If type inference is uncertain: Use conservative types with explicit uncertainty notes
- If YARD syntax validation fails: Provide corrected syntax with explanations
- Continue with partial documentation rather than failing completely

## References

Load `references/yard-patterns.md` for comprehensive YARD tag usage patterns,
type annotation standards, example generation guidelines, and common
documentation anti-patterns to avoid.
