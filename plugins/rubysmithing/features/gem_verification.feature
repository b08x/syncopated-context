@gem-verification
Feature: Gem Verification

  The Tester Agent validates gem existence against RubyGems API to prevent
  hallucinated recommendations from reaching the Builder.

  Background:
    Given the rubysmithing environment is initialized

  @valid-gem
  Scenario: Researcher recommends a valid gem
    Given the researcher recommends a gem "rspec"
    When I verify the gem against RubyGems API
    Then the gem should exist
    And the verification result should be cached

  @invalid-gem
  Scenario: Researcher recommends a non-existent gem
    Given the researcher recommends a gem "non-existent-fake-gem-xyz-123"
    When I verify the gem against RubyGems API
    Then the verification should fail
    And I should receive an error message

  @version-validation
  Scenario: Version-specific gem validation
    Given the researcher recommends gem "rails" with version "~> 7.0"
    When I verify the gem version against RubyGems API
    Then the version should be available
    And the latest compatible version should be returned

  @multiple-gems
  Scenario: Validate multiple gems from a Gemfile
    Given a Gemfile with the following gems:
      | name       | version  |
      | rake       | ~> 13.0  |
      | rspec      | ~> 3.12  |
      | concurrent-ruby | ~> 1.2 |
    When I verify all gems against RubyGems API
    Then all gems should exist
    And no version conflicts should be detected

  @bundle-testing
  Scenario: Test Gemfile bundle install
    Given a valid Gemfile exists at "spec/fixtures/test_gemfile.rb"
    When I run bundle install in an isolated environment
    Then the bundle install should succeed
    And all gems should be installed correctly

  @bundle-testing-failure
  Scenario: Test invalid Gemfile bundle install
    Given an invalid Gemfile exists at "spec/fixtures/invalid_gemfile.rb"
    When I run bundle install in an isolated environment
    Then the bundle install should fail
    And an appropriate error message should be returned