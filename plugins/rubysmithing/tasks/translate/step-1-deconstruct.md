# Translate — Step 1: Deconstruct Foreign Codebase

You are the `senior-backend-architect` executing Step 1 of the `/rubysmithing:translate` workflow.

## Your Task

Translate the provided foreign codebase (Python / React / Go / other) into a Ruby OOP blueprint. Produce no implementation code — blueprints only.

## Instructions

Follow your standard deconstruction process:
1. Identify paradigm gaps between the source language and idiomatic Ruby
2. Produce a Blueprint (module/class structure, method signatures, dependencies)
3. Produce an Object Graph (class relationships, data flow)
4. Produce a Translation Map (source construct → Ruby equivalent)
5. Produce Architectural Notes (what will be lost, what will be harder, paradigm mismatches)

## Output — 4 Artifacts

**Blueprint:**
```ruby
# Module/class stubs with method signatures
module AppName
  class ClassName
    # @param name [Type] description
    def method_name(param); end
  end
end
```

**Object Graph:** Class relationships as ASCII diagram or list

**Translation Map:**
| Source construct | Ruby equivalent | Notes |
|---|---|---|

**Architectural Notes:** Honest assessment of paradigm gaps and risks.

**Gem Requirements (for context-engineer):**
List every non-stdlib gem the Ruby implementation will need.
