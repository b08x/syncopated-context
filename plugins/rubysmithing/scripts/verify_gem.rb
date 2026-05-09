#!/usr/bin/env ruby
# frozen_string_literal: true

# rubysmithing-verify-gem: CLI tool wrapping the Verification::Integrator
#
# Provides manual testing capability for gem verification.
#
# @example Verify a gem exists
#   ruby scripts/verify_gem.rb rails
#
# @example Verify a version constraint
#   ruby scripts/verify_gem.rb rails "~> 7.0"
#
# @example Check a non-existent gem (shows suggestions)
#   ruby scripts/verify_gem.rb nonexistent_gem

require_relative "../lib/rubysmithing/verification/integrator"

def usage
  <<~USAGE
    Usage: verify_gem.rb <gem> [version_constraint] [--json]
    
    Commands:
      verify_gem.rb <gem>               Verify gem exists on RubyGems.org
      verify_gem.rb <gem> "~> 1.0"     Verify gem satisfies version constraint
      verify_gem.rb <gem> --json       Machine-readable JSON output
    
    Examples:
      ruby scripts/verify_gem.rb rails
      ruby scripts/verify_gem.rb rails "~> 7.0"
      ruby scripts/verify_gem.rb nonexistent_gem
    
    Exit codes:
      0 - Gem verified successfully
      1 - Gem not found or version constraint unsatisfiable
      2 - RubyGems.org unavailable, using stale cache
  USAGE
end

def format_result(result, gem_name, json_mode: false)
  if json_mode
    JSON.pretty_generate(
      status: result.status.to_s,
      gem: gem_name,
      gem_info: result.gem_info,
      error: result.error,
      suggestions: result.suggestions,
      staleness_warning: result.staleness_warning&.strip
    )
  else
    output = []
    output << case result.status
              when :verified
                "✓ Gem '#{gem_name}' verified on RubyGems.org"
              when :stale_fallback
                "⚠ Gem '#{gem_name}' verified via stale cache"
              when :not_found
                "✗ Gem '#{gem_name}' not found on RubyGems.org"
              when :unverified
                "✗ Gem '#{gem_name}' could not be verified"
              end

    if result.gem_info && result.status == :verified
      output << "  Version: #{result.gem_info[:version]}" if result.gem_info[:version]
      output << "  Description: #{result.gem_info[:description]&.slice(0, 80)}..." if result.gem_info[:description]
    end

    if result.staleness_warning
      output << "\n#{result.staleness_warning}"
    end

    if result.error
      output << "\n#{result.error}"
    end

    if result.suggestions&.any?
      output << "\nDid you mean: #{result.suggestions.join(', ')}?"
    end

    output.join("\n")
  end
end

def exit_code_for_status(status)
  case status
  when :verified then 0
  when :stale_fallback then 2
  else 1
  end
end

# Main CLI runner
if __FILE__ == $PROGRAM_NAME
  require "json"
  require "pp"

  args = ARGV.dup
  json_mode = args.delete("--json") || args.delete("-j")

  gem_name = args[0]
  unless gem_name
    puts usage
    exit 1
  end

  version_constraint = args[1]

  begin
    integrator = Rubysmithing::Verification::Integrator.new
    result = integrator.verify(gem_name, version_constraint)

    puts format_result(result, gem_name, json_mode: json_mode)
    exit exit_code_for_status(result.status)
  rescue => e
    if json_mode
      puts JSON.generate({ status: "error", gem: gem_name, error: e.message })
    else
      puts "Error: #{e.message}"
      puts e.backtrace.first(5).join("\n")
    end
    exit 1
  end
end