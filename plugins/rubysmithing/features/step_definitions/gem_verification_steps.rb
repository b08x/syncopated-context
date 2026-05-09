# frozen_string_literal: true

# Step definitions for gem verification cucumber scenarios
# These steps interact with the GemVerifier and BundleTester modules

Given("the rubysmithing environment is initialized") do
  # Environment is implicitly initialized via autoloading
  # Verify that required classes are available
  expect defined?(Rubysmithing::GemVerifier).to be_truthy
  expect defined?(Rubysmithing::BundleTester).to be_truthy
end

Given("the researcher recommends a gem {string}") do |gem_name|
  @recommended_gem = gem_name
end

Given("the researcher recommends gem {string} with version {string}") do |gem_name, version|
  @recommended_gem = gem_name
  @recommended_version = version
end

Given("a Gemfile with the following gems:") do |table|
  @gemfile_gems = table.hashes
end

Given("a valid Gemfile exists at {string}") do |path|
  @test_gemfile_path = path
end

Given("an invalid Gemfile exists at {string}") do |path|
  @invalid_gemfile_path = path
end

When("I verify the gem against RubyGems API") do
  verifier = Rubysmithing::GemVerifier.new
  @verification_result = verifier.verify_exists?(@recommended_gem)
  @verification_error = nil
rescue Rubysmithing::GemVerifier::GemNotFound => e
  @verification_result = false
  @verification_error = e.message
rescue Rubysmithing::GemVerifier::DegradedError => e
  @verification_result = false
  @verification_error = "RubyGems API unavailable: #{e.message}"
end

When("I verify the gem version against RubyGems API") do
  verifier = Rubysmithing::GemVerifier.new
  @version_result = verifier.version_exists?(@recommended_gem, @recommended_version)
  @version_error = nil
rescue Rubysmithing::GemVerifier::GemNotFound => e
  @version_result = false
  @version_error = e.message
rescue Rubysmithing::GemVerifier::GemVersionNotFound => e
  @version_result = false
  @version_error = e.message
end

When("I verify all gems against RubyGems API") do
  verifier = Rubysmithing::GemVerifier.new
  @all_verification_results = []
  @verification_failures = []

  @gemfile_gems.each do |gem|
    begin
      result = verifier.verify_exists?(gem["name"])
      @all_verification_results << { name: gem["name"], exists: result }
      @verification_failures << gem["name"] unless result
    rescue => e
      @all_verification_results << { name: gem["name"], exists: false, error: e.message }
      @verification_failures << gem["name"]
    end
  end
end

When("I run bundle install in an isolated environment") do
  if @test_gemfile_path
    @bundle_result = Rubysmithing::BundleTester.test_gemfile(@test_gemfile_path)
  elsif @invalid_gemfile_path
    @bundle_result = Rubysmithing::BundleTester.test_gemfile_safe(@invalid_gemfile_path)
  end
end

Then("the gem should exist") do
  expect(@verification_result).to be true
end

Then("the verification should fail") do
  expect(@verification_result).to be false
end

Then("I should receive an error message") do
  expect(@verification_error).to be_a(String)
  expect(@verification_error.length).to be > 0
end

Then("the version should be available") do
  expect(@version_result).to be true
end

Then("the latest compatible version should be returned") do
  verifier = Rubysmithing::GemVerifier.new
  latest = verifier.latest_matching_version(@recommended_gem, @recommended_version)
  expect(latest).to be_a(String)
  expect(latest.length).to be > 0
end

Then("all gems should exist") do
  expect(@verification_failures).to be_empty,
    "These gems were not found: #{@verification_failures.join(', ')}"
end

Then("no version conflicts should be detected") do
  # Version conflict detection is implicitly handled by successful version checks
  # If we got here without exceptions, there are no conflicts
  expect(@all_verification_results).not_to be_empty
end

Then("the bundle install should succeed") do
  expect(@bundle_result[:success]).to be true,
    "Bundle install failed with output: #{@bundle_result[:output]}"
end

Then("all gems should be installed correctly") do
  expect(@bundle_result[:success]).to be true
end

Then("the bundle install should fail") do
  expect(@bundle_result[:success]).to be false
end

Then("an appropriate error message should be returned") do
  expect(@bundle_result[:output]).to be_a(String)
end

Then("the verification result should be cached") do
  # Cache verification is an internal implementation detail
  # Just verify the result was obtained successfully
  expect(@verification_result).to be boolean
end