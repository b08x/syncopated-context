# frozen_string_literal: true

# rubysmithing-bundle-tester: Isolated Gemfile testing for rubysmithing artifacts
#
# This module provides a safe mechanism for testing Gemfile installations
# in an isolated temporary directory without polluting the host environment.
#
# @example Test a Gemfile
#   result = Rubysmithing::BundleTester.test_gemfile("/path/to/Gemfile")
#   puts result[:success]  # => true or false
#   puts result[:output]   # => stdout/stderr from bundle install

require "tmpdir"
require "fileutils"

module Rubysmithing
  class BundleTester
    # Exit codes for bundle install
    EXIT_SUCCESS = 0

    # Maximum time allowed for bundle install (seconds)
    BUNDLE_TIMEOUT = 120

    # Custom error class for bundle testing failures
    class BundleTestError < StandardError
      def initialize(message, gemfile_path: nil, exit_code: nil)
        super(message)
        @gemfile_path = gemfile_path
        @exit_code = exit_code
      end

      attr_reader :gemfile_path, :exit_code
    end

    # Tests a Gemfile by copying it to an isolated temp directory and running
    # bundle install. This ensures no side effects on the host environment.
    #
    # @param gemfile_path [String] Path to the Gemfile to test
    # @param bundler_args [Array<String>] Additional arguments to pass to bundle install
    # @return [Hash{Symbol => Object}] Result hash containing:
    #   - :success [Boolean] true if bundle install succeeded
    #   - :exit_code [Integer] the exit code from bundle install
    #   - :output [String] Combined stdout/stderr from bundle install
    #   - :gemfile_path [String] Path to the tested Gemfile
    #   - :tmp_dir [String] Path to the temporary directory used
    # @raise [BundleTestError] If the Gemfile cannot be read or doesn't exist
    def self.test_gemfile(gemfile_path, *bundler_args)
      validate_gemfile!(gemfile_path)

      Dir.mktmpdir do |tmpdir|
        copy_gemfile_to_tmpdir(gemfile_path, tmpdir)

        Dir.chdir(tmpdir) do
          result = run_bundle_install(bundler_args)
          return result
        end
      end
    rescue => e
      raise BundleTestError.new(e.message, gemfile_path: gemfile_path)
    end

    # Runs bundle install in the current directory with optional args
    # Returns a result hash without raising exceptions
    def self.test_gemfile_safe(gemfile_path, *bundler_args)
      test_gemfile(gemfile_path, *bundler_args)
    rescue BundleTestError => e
      {
        success: false,
        exit_code: e.exit_code || 1,
        output: e.message,
        gemfile_path: gemfile_path,
        tmp_dir: nil,
        error: e.class.name
      }
    end

    # Tests a Gemfile content string directly (useful for generated Gemfiles)
    #
    # @param gemfile_content [String] Content of the Gemfile
    # @param bundler_args [Array<String>] Additional arguments to pass to bundle install
    # @return [Hash{Symbol => Object}] Result hash (same as test_gemfile)
    def self.test_gemfile_content(gemfile_content, *bundler_args)
      Dir.mktmpdir do |tmpdir|
        gemfile_path = File.join(tmpdir, "Gemfile")
        File.write(gemfile_path, gemfile_content)

        Dir.chdir(tmpdir) do
          result = run_bundle_install(bundler_args)
          return result
        end
      end
    rescue => e
      raise BundleTestError.new(e.message)
    end

    private_class_method def self.validate_gemfile!(gemfile_path)
      unless File.exist?(gemfile_path)
        raise BundleTestError.new("Gemfile not found: #{gemfile_path}", gemfile_path: gemfile_path)
      end

      unless File.readable?(gemfile_path)
        raise BundleTestError.new("Gemfile not readable: #{gemfile_path}", gemfile_path: gemfile_path)
      end
    end

    private_class_method def self.copy_gemfile_to_tmpdir(gemfile_path, tmpdir)
      FileUtils.cp(gemfile_path, File.join(tmpdir, "Gemfile"))

      # Also copy Gemfile.lock if it exists
      lockfile = gemfile_path.sub(/\.rb$/, ".lock").gsub("Gemfile", "Gemfile.lock")
      if File.exist?(lockfile)
        FileUtils.cp(lockfile, File.join(tmpdir, "Gemfile.lock"))
      end
    end

    private_class_method def self.run_bundle_install(bundler_args)
      output = +""
      exit_code = nil

      # Build bundle install command
      cmd = ["bundle", "install", "--quiet"]
      cmd.concat(bundler_args) unless bundler_args.empty?

      # Run bundle install and capture output
      Open3.pipeline_rw(cmd, err: [:child, :out]) do |stdin, stdout_stderr, wait_threads|
        stdin.close_write
        output = stdout_stderr.read
        stdout_stderr.close
        exit_code = wait_threads.value.exit_code
      end

      {
        success: exit_code == EXIT_SUCCESS,
        exit_code: exit_code,
        output: output,
        tmp_dir: Dir.pwd
      }
    rescue => e
      # If Open3.pipeline_rw fails, try a simpler approach
      require "open3"
      stdout, stderr, status = Open3.capture3(*cmd)
      {
        success: status.success?,
        exit_code: status.exitstatus,
        output: [stdout, stderr].join("\n"),
        tmp_dir: Dir.pwd
      }
    end
  end
end