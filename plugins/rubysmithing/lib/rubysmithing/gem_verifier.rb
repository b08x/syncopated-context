# frozen_string_literal: true

# rubysmithing-gem-verifier: RubyGems.org API client for gem metadata and version verification
#
# This module provides a stdlib-only client for interacting with the RubyGems.org API.
# It supports fetching gem metadata, version listing, and version constraint checking
# with Bundler-style operators.
#
# @example Basic usage
#   verifier = Rubysmithing::GemVerifier.new
#   info = verifier.get_gem_info("rails")
#   puts info[:version]  # => "7.1.3.2"
#
# @example Version constraint checking
#   verifier = Rubysmithing::GemVerifier.new
#   if verifier.version_exists?("rails", "~> 7.0")
#     puts "Rails 7.x is available"
#   end
#
# @example CLI usage
#   ruby lib/rubysmithing/gem_verifier.rb verify rails
#   ruby lib/rubysmithing/gem_verifier.rb versions sinatra
#   ruby lib/rubysmithing/gem_verifier.rb info rails

require "net/http"
require "json"

module Rubysmithing
  class GemVerifier
    RUBYGEMS_API_HOST = "https://rubygems.org"
    API_VERSION_PATH  = "/api/v1/gems"
    VERSION_PATH      = "/api/v1/versions"
    SPECS_PATH        = "/api/v1/specs.json"

    MAX_RETRIES      = 3
    BASE_DELAY_SECS  = 1
    TIMEOUT_SECONDS  = 10

    # Custom error classes for gem verification failures
    class GemNotFound < StandardError
      def initialize(gem_name)
        super("Gem not found on RubyGems.org: #{gem_name}")
      end
    end

    class GemVersionNotFound < StandardError
      def initialize(gem_name, constraint, reason = nil)
        msg = "No version of #{gem_name} satisfies constraint: #{constraint}"
        msg += ". #{reason}" if reason
        super(msg)
      end
    end

    class RubyGemsAPIError < StandardError
      def initialize(message, status_code: nil, gem_name: nil)
        super(message)
        @status_code = status_code
        @gem_name = gem_name
      end

      attr_reader :status_code, :gem_name
    end

    class DegradedError < StandardError
      def initialize(cause, hint = "Check network connectivity and RubyGems.org status")
        super("RubyGems.org is unreachable. #{hint}")
        @cause = cause
      end

      attr_reader :cause
    end

    # @param http_client [Net::HTTP] Optional HTTP client for dependency injection
    def initialize(http_client: nil)
      @http_client = http_client
    end

    # Fetches gem metadata from RubyGems.org
    #
    # @param gem_name [String] The name of the gem
    # @return [Hash{Symbol => Object}] Gem metadata including :name, :version, :description,
    #   :homepage, :source_code_uri, :licenses
    # @raise [GemNotFound] If the gem does not exist on RubyGems.org
    # @raise [RubyGemsAPIError] On HTTP errors (except 404)
    # @raise [DegradedError] If RubyGems.org is unreachable after retries
    def get_gem_info(gem_name)
      response = api_get("#{API_VERSION_PATH}/#{gem_name}.json")
      JSON.parse(response.body, symbolize_names: true)
    rescue GemNotFound => e
      raise
    rescue RubyGemsAPIError => e
      raise
    rescue => e
      raise DegradedError.new(e)
    end

    # Returns all available version strings for a gem
    #
    # @param gem_name [String] The name of the gem
    # @return [Array<String>] Array of version strings (e.g., ["1.0.0", "1.1.0", "2.0.0"])
    # @raise [GemNotFound] If the gem does not exist on RubyGems.org
    # @raise [RubyGemsAPIError] On HTTP errors (except 404)
    # @raise [DegradedError] If RubyGems.org is unreachable after retries
    def get_versions(gem_name)
      response = api_get("#{VERSION_PATH}/#{gem_name}.json")
      JSON.parse(response.body).map { |entry| entry["number"] }
    rescue GemNotFound => e
      raise
    rescue RubyGemsAPIError => e
      raise
    rescue => e
      raise DegradedError.new(e)
    end

    # Fast boolean check if a gem exists on RubyGems.org
    #
    # @param gem_name [String] The name of the gem
    # @return [Boolean] true if gem exists, false otherwise
    def verify_exists?(gem_name)
      api_get("#{API_VERSION_PATH}/#{gem_name}.json")
      true
    rescue GemNotFound
      false
    rescue RubyGemsAPIError
      false
    rescue DegradedError
      false
    end

    # Checks if any version of the gem satisfies the given version constraint
    #
    # @param gem_name [String] The name of the gem
    # @param constraint [String] A Bundler-style version constraint
    #   (e.g., "~> 2.1", ">= 3.0", ">= 1.0, < 2.0")
    # @return [Boolean] true if constraint can be satisfied
    # @raise [GemNotFound] If the gem does not exist on RubyGems.org
    # @raise [GemVersionNotFound] If no version satisfies the constraint (with reason)
    # @raise [RubyGemsAPIError] On HTTP errors (except 404)
    # @raise [DegradedError] If RubyGems.org is unreachable after retries
    def version_exists?(gem_name, constraint)
      versions = get_versions(gem_name)
      return false if versions.empty?

      parsed_constraint = VersionConstraint.parse(constraint)
      matching = versions.select { |v| parsed_constraint.satisfied_by?(v) }

      if matching.empty?
        latest = versions.max { |a, b| Gem::Version.new(a) <=> Gem::Version.new(b) }
        reason = generate_constraint_reason(parsed_constraint, versions, latest)
        raise GemVersionNotFound.new(gem_name, constraint, reason)
      end

      true
    end

    # Returns the latest version satisfying a constraint, or nil
    #
    # @param gem_name [String] The name of the gem
    # @param constraint [String] A Bundler-style version constraint
    # @return [String, nil] The latest matching version string
    # @raise [GemNotFound] If the gem does not exist
    # @raise [GemVersionNotFound] If no version satisfies the constraint
    def latest_matching_version(gem_name, constraint)
      versions = get_versions(gem_name)
      return nil if versions.empty?

      parsed_constraint = VersionConstraint.parse(constraint)
      matching = versions.select { |v| parsed_constraint.satisfied_by?(v) }

      if matching.empty?
        latest = versions.max { |a, b| Gem::Version.new(a) <=> Gem::Version.new(b) }
        reason = generate_constraint_reason(parsed_constraint, versions, latest)
        raise GemVersionNotFound.new(gem_name, constraint, reason)
      end

      matching.max { |a, b| Gem::Version.new(a) <=> Gem::Version.new(b) }
    end

    private

    def http
      @http_client || Net::HTTP
    end

    def api_get(path, retries: MAX_RETRIES, delay: BASE_DELAY_SECS)
      uri = URI.parse("#{RUBYGEMS_API_HOST}#{path}")

      request = Net::HTTP::Get.new(uri)
      request["Accept"] = "application/json"
      request["User-Agent"] = "rubysmithing-gem-verifier/1.0"

      response = http.start(uri.host, uri.port, use_ssl: uri.scheme == "https") do |conn|
        conn.open_timeout = TIMEOUT_SECONDS
        conn.read_timeout = TIMEOUT_SECONDS
        conn.request(request)
      end

      handle_response(response, path)
    rescue Net::OpenTimeout, Net::ReadTimeout, SocketError, Errno::ECONNRESET, Errno::ECONNREFUSED => e
      handle_network_error(e, retries, delay, path)
    end

    def handle_response(response, path)
      case response
      when Net::HTTPSuccess
        response
      when Net::HTTPNotFound
        gem_name = extract_gem_name_from_path(path)
        raise GemNotFound.new(gem_name)
      when Net::HTTPTooManyRequests
        raise RubyGemsAPIError.new(
          "Rate limit exceeded on RubyGems.org",
          status_code: 429,
          gem_name: extract_gem_name_from_path(path)
        )
      when Net::HTTPInternalServerError, Net::HTTPBadGateway,
           Net::HTTPServiceUnavailable, Net::HTTPGatewayTimeout
        raise RubyGemsAPIError.new(
          "RubyGems.org server error: #{response.class::RESPONSE_WELCOME_KEY}",
          status_code: response.code.to_i,
          gem_name: extract_gem_name_from_path(path)
        )
      else
        raise RubyGemsAPIError.new(
          "Unexpected response from RubyGems.org: #{response.class}",
          status_code: response.code.to_i,
          gem_name: extract_gem_name_from_path(path)
        )
      end
    end

    def handle_network_error(e, retries, delay, path)
      if retries.positive?
        sleep(delay)
        api_get(path, retries: retries - 1, delay: delay * 2)
      else
        raise DegradedError.new(e)
      end
    end

    def extract_gem_name_from_path(path)
      path.split("/").reject(&:empty?).last&.gsub(".json", "") || "unknown"
    end

    def generate_constraint_reason(constraint, all_versions, latest)
      requirements = constraint.requirements
      reasons = []

      requirements.each do |op, ver|
        case op
        when :>=
          reasons << "requires version >= #{ver}"
        when :<
          reasons << "requires version < #{ver}"
        when :<=
          reasons << "requires version <= #{ver}"
        when :==
          reasons << "requires version == #{ver}"
        when "~>"
          reasons << "requires version ~> #{ver} (pessimistic)"
        end
      end

      available = "Available versions: #{all_versions.last(5).join(', ')}"
      available += " (latest: #{latest})" if latest

      "#{reasons.join('; ')}. #{available}"
    end

    # Bundler-style version constraint parser
    class VersionConstraint
      attr_reader :requirements

      def initialize(requirements)
        @requirements = requirements # Array of [operator, version] pairs
      end

      # Parse a constraint string into a VersionConstraint object
      # Supports: "> 2.0", ">= 1.0, < 2.0", ">~> 1.2" (pessimistic)
      def self.parse(constraint_string)
        return new([]) if constraint_string.nil? || constraint_string.empty?

        requirements = []
        parts = constraint_string.split(",").map(&:strip)

        parts.each do |part|
          requirements << parse_single(part)
        end

        new(requirements)
      end

      def self.parse_single(part)
        # Pessimistic constraint: ~> 1.2
        if part.start_with?("~>")
          version_str = part[3..].strip
          version = Gem::Version.new(version_str)
          major = version.segments[0] || 0
          minor = version.segments[1] || 0
          # ~> 1.2 means >= 1.2 and < (major + 1) if minor == 0, else < major.minor + 1
          if minor.zero?
            [[:>=, version], [:<, Gem::Version.new("#{major + 1}.0.0")]]
          else
            [[:>=, version], [:<, Gem::Version.new("#{major}.#{minor + 1}.0")]]
          end
        elsif part.start_with?(">=")
          version_str = part[2..].strip
          [[:>=, Gem::Version.new(version_str)]]
        elsif part.start_with?("<=")
          version_str = part[2..].strip
          [[:<=, Gem::Version.new(version_str)]]
        elsif part.start_with?(">")
          version_str = part[1..].strip
          [[:>, Gem::Version.new(version_str)]]
        elsif part.start_with?("<")
          version_str = part[1..].strip
          [[:<, Gem::Version.new(version_str)]]
        elsif part.start_with?("==")
          version_str = part[2..].strip
          [[:==, Gem::Version.new(version_str)]]
        else
          # Assume exact version
          [[:==, Gem::Version.new(part)]]
        end
      end

      def satisfied_by?(version_string)
        return true if requirements.empty?

        gem_version = Gem::Version.new(version_string)

        requirements.all? do |op, ver|
          case op
          when :>=
            gem_version >= ver
          when :<
            gem_version < ver
          when :<=
            gem_version <= ver
          when :>
            gem_version > ver
          when :==
            gem_version == ver
          when "~>"
            # Pessimistic: >= ver and < next_major_minor
            if ver.segments[1].zero?
              gem_version >= ver && gem_version < Gem::Version.new("#{ver.segments[0] + 1}.0.0")
            else
              gem_version >= ver && gem_version < Gem::Version.new("#{ver.segments[0]}.#{ver.segments[1] + 1}.0")
            end
          else
            false
          end
        end
      end
    end
  end
end

# CLI runner
if __FILE__ == $PROGRAM_NAME
  require "pp"

  def usage
    <<~USAGE
      Usage: ruby gem_verifier.rb <command> [options]

      Commands:
        verify <gem>          Check if gem exists (exit 0 if yes, 1 if no)
        versions <gem>        List all versions of a gem
        info <gem>            Show detailed gem metadata
        check <gem> <constraint>  Check if constraint is satisfiable

      Examples:
        ruby lib/rubysmithing/gem_verifier.rb verify rails
        ruby lib/rubysmithing/gem_verifier.rb versions sinatra
        ruby lib/rubysmithing/gem_verifier.rb info aws-sdk-s3
        ruby lib/rubysmithing/gem_verifier.rb check rails "~> 7.0"
    USAGE
  end

  verifier = Rubysmithing::GemVerifier.new

  args = ARGV.dup
  json_mode = args.delete("--json") || args.delete("-j")

  case args[0]
  when "verify"
    gem_name = args[1]
    abort "Usage: verify <gem_name>" unless gem_name

    if verifier.verify_exists?(gem_name)
      puts json_mode ? JSON.generate({ status: "exists", gem: gem_name }) : "Gem exists: #{gem_name}"
      exit 0
    else
      puts json_mode ? JSON.generate({ status: "not_found", gem: gem_name }) : "Gem not found: #{gem_name}"
      exit 1
    end

  when "versions"
    gem_name = args[1]
    abort "Usage: versions <gem_name>" unless gem_name

    versions = verifier.get_versions(gem_name)
    if json_mode
      puts JSON.generate({ status: "ok", gem: gem_name, versions: versions })
    else
      puts "Versions for #{gem_name}:"
      versions.each { |v| puts "  #{v}" }
    end

  when "info"
    gem_name = args[1]
    abort "Usage: info <gem_name>" unless gem_name

    info = verifier.get_gem_info(gem_name)
    if json_mode
      puts JSON.generate(info.transform_keys(&:to_s))
    else
      puts "Gem: #{info[:name]}"
      puts "Version: #{info[:version]}"
      puts "Description: #{info[:description]}"
      puts "Homepage: #{info[:homepage]}"
      puts "Source Code: #{info[:source_code_uri]}"
      puts "Licenses: #{info[:licenses]}"
    end

  when "check"
    gem_name = args[1]
    constraint = args[2]
    abort "Usage: check <gem_name> <constraint>" unless gem_name && constraint

    begin
      verifier.version_exists?(gem_name, constraint)
      puts json_mode ? JSON.generate({ status: "satisfiable", gem: gem_name, constraint: constraint }) \
                    : "Constraint satisfiable: #{gem_name} #{constraint}"
      exit 0
    rescue Rubysmithing::GemVersionNotFound => e
      puts json_mode ? JSON.generate({ status: "unsatisfiable", gem: gem_name, constraint: constraint, reason: e.message }) \
                    : e.message
      exit 1
    rescue Rubysmithing::GemNotFound => e
      puts json_mode ? JSON.generate({ status: "not_found", gem: gem_name }) : e.message
      exit 1
    end

  else
    puts usage
    exit 1
  end
end