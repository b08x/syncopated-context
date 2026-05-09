# frozen_string_literal: true

require "rspec"

RSpec.configure do |config|
  config.expect_with :rspec do |expectations|
    expectations.syntax = [:expect]
  end

  config.mock_with :rspec do |mocks|
    mocks.syntax = [:expect]
  end

  config.disable_monkey_patching!
  config.expose_dsl_globally = false
end