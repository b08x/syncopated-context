# frozen_string_literal: true

# rubysmithing-verification-integrator: Integrates gem verification with researcher workflow
#
# This module wraps the GemVerifier and ContextCache to provide a unified
# verification entry point for the researcher workflow. It gates on RubyGems.org
# existence before any caching occurs.
#
# @example Basic usage
#   result = Rubysmithing::Verification::Integrator.verify("rails")
#   puts result.status  # => :verified
#   puts result.gem_info[:version]  # => "7.1.3.2"
#
# @example With version constraint
#   result = Rubysmithing::Verification::Integrator.verify("rails", "~> 7.0")
#   puts result.status  # => :verified
#
# @example Gem not found
#   result = Rubysmithing::Verification::Integrator.verify("nonexistent_gem")
#   puts result.status  # => :not_found
#   puts result.suggestions  # => ["rails", "rake", "rspec"]

require_relative "../gem_verifier"
require_relative "../../scripts/context_cache"

module Rubysmithing
  module Verification
    # Result struct returned from {Integrator.verify}
    VerificationResult = Struct.new(
      :status,
      :gem_info,
      :error,
      :suggestions,
      :staleness_warning,
      keyword_init: true
    ) do
      # @return [Symbol] One of: :verified, :stale_fallback, :unverified, :not_found
      attr_accessor :status

      # @return [Hash, nil] Gem metadata from RubyGems.org or cache
      attr_accessor :gem_info

      # @return [String, nil] Error message if verification failed
      attr_accessor :error

      # @return [Array<String>, nil] Suggested gem names if not found
      attr_accessor :suggestions

      # @return [String, nil] Staleness warning for stale cache entries
      attr_accessor :staleness_warning

      def verified?
        status == :verified
      end

      def stale_fallback?
        status == :stale_fallback
      end

      def not_found?
        status == :not_found
      end
    end

    class Integrator
      SEARCH_API_HOST = "https://rubygems.org"
      SEARCH_PATH     = "/api/v1/search.json"
      MAX_SUGGESTIONS = 3

      # @param gem_verifier [GemVerifier] Optional GemVerifier instance
      # @param context_cache [ContextCache] Optional ContextCache instance
      def initialize(gem_verifier: nil, context_cache: nil)
        @gem_verifier = gem_verifier || GemVerifier.new
        @context_cache = context_cache || ContextCache.new
      end

      # Primary entry point for researcher workflow.
      #
      # Workflow:
      # 1. Try gem_verifier.verify_exists?(gem_name)
      # 2. If API unavailable (DegradedError), fall back to ContextCache fetch_stale
      # 3. If no cache entry exists either, return an error with suggested alternatives
      #
      # @param gem_name [String] The name of the gem to verify
      # @param version_constraint [String, nil] Optional version constraint to check
      # @return [VerificationResult] The verification result
      def verify(gem_name, version_constraint = nil)
        # Step 1: Try RubyGems.org API first
        begin
          if version_constraint
            verified_with_constraint(gem_name, version_constraint)
          else
            verified_without_constraint(gem_name)
          end
        rescue GemVerifier::DegradedError => e
          # Step 2: API unavailable — fall back to stale cache
          fallback_to_stale_cache(gem_name)
        rescue GemVerifier::GemNotFound
          # Step 3: Gem doesn't exist — generate suggestions
          suggestions = fetch_suggestions(gem_name)
          VerificationResult.new(
            status: :not_found,
            error: "Gem '#{gem_name}' not found on RubyGems.org.",
            suggestions: suggestions
          )
        rescue GemVerifier::GemVersionNotFound => e
          # Version constraint failed
          VerificationResult.new(
            status: :unverified,
            error: build_version_error_message(gem_name, version_constraint, e),
            suggestions: nil
          )
        rescue GemVerifier::RubyGemsAPIError => e
          # API error — try stale cache
          fallback_to_stale_cache(gem_name)
        end
      end

      private

      def verified_without_constraint(gem_name)
        exists = @gem_verifier.verify_exists?(gem_name)
        return not_found_result(gem_name) unless exists

        gem_info = @gem_verifier.get_gem_info(gem_name)
        VerificationResult.new(
          status: :verified,
          gem_info: gem_info,
          error: nil,
          suggestions: nil,
          staleness_warning: nil
        )
      end

      def verified_with_constraint(gem_name, constraint)
        @gem_verifier.version_exists?(gem_name, constraint)
        gem_info = @gem_verifier.get_gem_info(gem_name)
        VerificationResult.new(
          status: :verified,
          gem_info: gem_info,
          error: nil,
          suggestions: nil,
          staleness_warning: nil
        )
      end

      def fallback_to_stale_cache(gem_name)
        entry = @context_cache.fetch_stale(gem_name)
        if entry
          warning = @context_cache.staleness_warning(gem_name, entry: entry)
          VerificationResult.new(
            status: :stale_fallback,
            gem_info: entry,
            error: nil,
            suggestions: nil,
            staleness_warning: warning
          )
        else
          suggestions = fetch_suggestions(gem_name)
          VerificationResult.new(
            status: :unverified,
            error: "Gem '#{gem_name}' could not be verified (RubyGems.org unavailable and no cached data).",
            suggestions: suggestions
          )
        end
      end

      def not_found_result(gem_name)
        suggestions = fetch_suggestions(gem_name)
        VerificationResult.new(
          status: :not_found,
          gem_info: nil,
          error: "Gem '#{gem_name}' not found on RubyGems.org.",
          suggestions: suggestions
        )
      end

      def fetch_suggestions(gem_name)
        search_gems(gem_name)
      rescue => e
        # If search fails, return empty array — don't let search errors bubble up
        []
      end

      def search_gems(query)
        uri = URI.parse("#{SEARCH_API_HOST}#{SEARCH_PATH}?query=#{URI.encode_www_form_component(query)}")
        request = Net::HTTP::Get.new(uri)
        request["Accept"] = "application/json"
        request["User-Agent"] = "rubysmithing-verification-integrator/1.0"

        response = Net::HTTP.start(uri.host, uri.port, use_ssl: uri.scheme == "https") do |conn|
          conn.open_timeout = 5
          conn.read_timeout = 5
          conn.request(request)
        end

        return [] unless response.is_a?(Net::HTTPSuccess)

        results = JSON.parse(response.body)
        results.first(MAX_SUGGESTIONS).map { |r| r["name"] }
      rescue => e
        []
      end

      def build_version_error_message(gem_name, constraint, error)
        versions = @gem_verifier.get_versions(gem_name)
        latest = versions.max { |a, b| Gem::Version.new(a) <=> Gem::Version.new(b) }
        available = versions.last(5).join(", ")

        "Gem '#{gem_name}' version constraint '#{constraint}' cannot be satisfied. " \
          "Available versions: [#{available}]. Latest: #{latest}."
      end
    end
  end
end