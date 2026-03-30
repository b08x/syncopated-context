# frozen_string_literal: true

# app.rb — entry point
# Replace APP_NAME and app_name with your application name throughout

require "zeitwerk"
require "bundler/setup"

APP_NAME = "MyApp" # TODO: replace

loader = Zeitwerk::Loader.new
loader.push_dir("#{__dir__}/lib")
loader.setup

Bubbletea.run(AppName::App.new)
