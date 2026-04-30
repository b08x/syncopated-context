# frozen_string_literal: true

require "bundler/setup"
require "dotenv"
require "zeitwerk"

# Load environment variables
Dotenv.load

# Configure Zeitwerk loader
loader = Zeitwerk::Loader.new
loader.push_dir(File.expand_path("../lib", __dir__))
loader.setup

# Initialize Database
require_relative "../lib/rubysmithing/database"
DB = Rubysmithing::Database.connect
