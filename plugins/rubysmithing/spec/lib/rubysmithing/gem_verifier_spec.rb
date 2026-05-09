# frozen_string_literal: true

require_relative "../../../lib/rubysmithing/gem_verifier"
require_relative "../../../spec_helper"

RSpec.describe Rubysmithing::GemVerifier do
  let(:gem_verifier) { described_class.new(http_client: fake_http) }
  let(:fake_http) { instance_double("Net::HTTP") }

  describe "#verify_exists?" do
    context "when gem exists" do
      let(:success_response) do
        response = Net::HTTPOK.new("1.0", "200", "OK")
        allow(response).to receive(:body) { '{"name":"rails","version":"7.1.3.2"}' }
        response
      end

      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request) { success_response }
      end

      it "returns true" do
        expect(gem_verifier.verify_exists?("rails")).to be true
      end
    end

    context "when gem does not exist" do
      let(:not_found_response) do
        Net::HTTPNotFound.new("1.0", "404", "Not Found")
      end

      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request) { not_found_response }
      end

      it "returns false" do
        expect(gem_verifier.verify_exists?("nonexistent_gem_xyz")).to be false
      end
    end

    context "when network error occurs" do
      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request).and_raise(Net::OpenTimeout.new("Connection timed out"))
      end

      it "returns false" do
        expect(gem_verifier.verify_exists?("rails")).to be false
      end
    end
  end

  describe "#get_gem_info" do
    let(:gem_info_response) do
      response = Net::HTTPOK.new("1.0", "200", "OK")
      allow(response).to receive(:body) do
        {
          name: "rails",
          version: "7.1.3.2",
          description: "Ruby on Rails framework",
          homepage: "https://rubyonrails.org",
          source_code_uri: "https://github.com/rails/rails",
          licenses: ["MIT"]
        }.to_json
      end
      response
    end

    before do
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { gem_info_response }
    end

    it "returns parsed gem metadata" do
      info = gem_verifier.get_gem_info("rails")
      expect(info[:name]).to eq("rails")
      expect(info[:version]).to eq("7.1.3.2")
      expect(info[:description]).to eq("Ruby on Rails framework")
      expect(info[:homepage]).to eq("https://rubyonrails.org")
      expect(info[:source_code_uri]).to eq("https://github.com/rails/rails")
    end

    it "raises GemNotFound for 404 response" do
      not_found = Net::HTTPNotFound.new("1.0", "404", "Not Found")
      allow(fake_http).to receive(:request) { not_found }

      expect { gem_verifier.get_gem_info("nonexistent_gem") }.to raise_error(Rubysmithing::GemVerifier::GemNotFound)
    end

    it "raises RubyGemsAPIError for rate limit" do
      rate_limited = Net::HTTPTooManyRequests.new("1.0", "429", "Too Many Requests")
      allow(fake_http).to receive(:request) { rate_limited }

      expect { gem_verifier.get_gem_info("rails") }.to raise_error(Rubysmithing::GemVerifier::RubyGemsAPIError) do |error|
        expect(error.status_code).to eq(429)
      end
    end
  end

  describe "#get_versions" do
    let(:versions_response) do
      response = Net::HTTPOK.new("1.0", "200", "OK")
      allow(response).to receive(:body) do
        [
          { "number" => "1.0.0" },
          { "number" => "1.1.0" },
          { "number" => "2.0.0" },
          { "number" => "2.1.0" }
        ].to_json
      end
      response
    end

    before do
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { versions_response }
    end

    it "returns array of version strings" do
      versions = gem_verifier.get_versions("rails")
      expect(versions).to match_array(["1.0.0", "1.1.0", "2.0.0", "2.1.0"])
    end
  end

  describe "#version_exists?" do
    context "with exact version constraint" do
      let(:versions_response) do
        response = Net::HTTPOK.new("1.0", "200", "OK")
        allow(response).to receive(:body) do
          [
            { "number" => "1.0.0" },
            { "number" => "1.1.0" },
            { "number" => "2.0.0" }
          ].to_json
        end
        response
      end

      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request) { versions_response }
      end

      it "returns true when exact version exists" do
        expect(gem_verifier.version_exists?("rails", "1.1.0")).to be true
      end

      it "returns false when exact version does not exist" do
        expect { gem_verifier.version_exists?("rails", "1.2.0") }.to raise_error(Rubysmithing::GemVerifier::GemVersionNotFound)
      end
    end

    context "with greater-than-or-equal constraint" do
      let(:versions_response) do
        response = Net::HTTPOK.new("1.0", "200", "OK")
        allow(response).to receive(:body) do
          [
            { "number" => "1.0.0" },
            { "number" => "1.5.0" },
            { "number" => "2.0.0" }
          ].to_json
        end
        response
      end

      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request) { versions_response }
      end

      it "returns true when version satisfies" do
        expect(gem_verifier.version_exists?("rails", ">= 1.5.0")).to be true
      end

      it "raises GemVersionNotFound when no version satisfies" do
        expect { gem_verifier.version_exists?("rails", ">= 3.0.0") }.to raise_error(Rubysmithing::GemVerifier::GemVersionNotFound) do |error|
          expect(error.message).to include("requires version >= 3.0.0")
        end
      end
    end

    context "with twiddle-wak constraint" do
      let(:versions_response) do
        response = Net::HTTPOK.new("1.0", "200", "OK")
        allow(response).to receive(:body) do
          [
            { "number" => "0.9.0" },
            { "number" => "1.0.0" },
            { "number" => "1.1.0" },
            { "number" => "2.0.0" },
            { "number" => "2.1.0" }
          ].to_json
        end
        response
      end

      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request) { versions_response }
      end

      it "returns true when version range includes available versions" do
        expect(gem_verifier.version_exists?("rails", ">= 1.0.0, < 2.0.0")).to be true
      end

      it "raises GemVersionNotFound when constraint cannot be satisfied" do
        expect { gem_verifier.version_exists?("rails", ">= 2.5.0, < 3.0.0") }.to raise_error(Rubysmithing::GemVerifier::GemVersionNotFound)
      end
    end

    context "with pessimistic constraint" do
      let(:versions_response) do
        response = Net::HTTPOK.new("1.0", "200", "OK")
        allow(response).to receive(:body) do
          [
            { "number" => "1.0.0" },
            { "number" => "1.1.0" },
            { "number" => "1.2.0" },
            { "number" => "1.2.1" },
            { "number" => "2.0.0" }
          ].to_json
        end
        response
      end

      before do
        allow(fake_http).to receive(:start).and_yield(fake_http)
        allow(fake_http).to receive(:open_timeout=)
        allow(fake_http).to receive(:read_timeout=)
        allow(fake_http).to receive(:request) { versions_response }
      end

      it "returns true when ~> 1.2 matches available versions" do
        # ~> 1.2 means >= 1.2 and < 2.0
        expect(gem_verifier.version_exists?("rails", "~> 1.2")).to be true
      end

      it "raises GemVersionNotFound when pessimistic constraint not satisfiable" do
        # ~> 2.0 means >= 2.0 and < 3.0, but only 1.x versions available
        expect { gem_verifier.version_exists?("rails", "~> 2.0") }.to raise_error(Rubysmithing::GemVerifier::GemVersionNotFound)
      end
    end
  end

  describe "#latest_matching_version" do
    let(:versions_response) do
      response = Net::HTTPOK.new("1.0", "200", "OK")
      allow(response).to receive(:body) do
        [
          { "number" => "1.0.0" },
          { "number" => "1.1.0" },
          { "number" => "2.0.0" },
          { "number" => "2.1.0" }
        ].to_json
      end
      response
    end

    before do
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { versions_response }
    end

    it "returns the latest matching version" do
      version = gem_verifier.latest_matching_version("rails", "~> 1.0")
      expect(version).to eq("1.1.0")
    end

    it "raises GemVersionNotFound when no version matches" do
      expect { gem_verifier.latest_matching_version("rails", "~> 5.0") }.to raise_error(Rubysmithing::GemVersionNotFound)
    end
  end

  describe "#latest_matching_version edge case" do
    let(:versions_response) do
      response = Net::HTTPOK.new("1.0", "200", "OK")
      allow(response).to receive(:body) do
        [{ "number" => "3.0.0" }].to_json
      end
      response
    end

    before do
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { versions_response }
    end

    it "handles gems with single version correctly" do
      version = gem_verifier.latest_matching_version("rails", ">= 2.0")
      expect(version).to eq("3.0.0")
    end
  end

  describe Rubysmithing::GemVerifier::VersionConstraint do
    describe "#satisfied_by?" do
      it "handles exact version matching" do
        constraint = described_class.parse("1.2.3")
        expect(constraint.satisfied_by?("1.2.3")).to be true
        expect(constraint.satisfied_by?("1.2.4")).to be false
      end

      it "handles >= constraint" do
        constraint = described_class.parse(">= 1.2.0")
        expect(constraint.satisfied_by?("1.2.0")).to be true
        expect(constraint.satisfied_by?("1.3.0")).to be true
        expect(constraint.satisfied_by?("1.1.0")).to be false
      end

      it "handles > constraint" do
        constraint = described_class.parse("> 1.2.0")
        expect(constraint.satisfied_by?("1.2.1")).to be true
        expect(constraint.satisfied_by?("1.2.0")).to be false
        expect(constraint.satisfied_by?("1.3.0")).to be true
      end

      it "handles < constraint" do
        constraint = described_class.parse("< 2.0.0")
        expect(constraint.satisfied_by?("1.9.9")).to be true
        expect(constraint.satisfied_by?("2.0.0")).to be false
      end

      it "handles <= constraint" do
        constraint = described_class.parse("<= 2.0.0")
        expect(constraint.satisfied_by?("2.0.0")).to be true
        expect(constraint.satisfied_by?("2.0.1")).to be false
      end

      it "handles twiddle-wak (range) constraint" do
        constraint = described_class.parse(">= 1.0.0, < 2.0.0")
        expect(constraint.satisfied_by?("1.5.0")).to be true
        expect(constraint.satisfied_by?("2.0.0")).to be false
        expect(constraint.satisfied_by?("0.9.0")).to be false
      end

      it "handles pessimistic constraint ~> 1.2" do
        constraint = described_class.parse("~> 1.2")
        # >= 1.2 and < 2.0
        expect(constraint.satisfied_by?("1.2.0")).to be true
        expect(constraint.satisfied_by?("1.3.0")).to be true
        expect(constraint.satisfied_by?("1.9.9")).to be true
        expect(constraint.satisfied_by?("2.0.0")).to be false
        expect(constraint.satisfied_by?("1.1.0")).to be false
      end

      it "handles pessimistic constraint ~> 1.0 with zero minor" do
        constraint = described_class.parse("~> 1.0")
        # >= 1.0 and < 2.0
        expect(constraint.satisfied_by?("1.0.0")).to be true
        expect(constraint.satisfied_by?("1.5.0")).to be true
        expect(constraint.satisfied_by?("2.0.0")).to be false
      end

      it "handles multiple constraints joined by comma" do
        constraint = described_class.parse(">= 1.0.0, < 2.0.0, != 1.5.0")
        expect(constraint.satisfied_by?("1.3.0")).to be true
        expect(constraint.satisfied_by?("1.5.0")).to be false
        expect(constraint.satisfied_by?("2.0.0")).to be false
      end

      it "handles empty constraint (always satisfied)" do
        constraint = described_class.parse("")
        expect(constraint.satisfied_by?("1.0.0")).to be true
        expect(constraint.satisfied_by?("999.0.0")).to be true
      end
    end
  end

  describe "DegradedError" do
    it "is raised after max retries exhausted on network error" do
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request).and_raise(Net::OpenTimeout.new("Connection timed out"))

      expect { gem_verifier.get_versions("rails") }.to raise_error(Rubysmithing::GemVerifier::DegradedError) do |error|
        expect(error.cause).to be_a(Net::OpenTimeout)
        expect(error.message).to include("Check network connectivity")
      end
    end
  end

  describe "Server error handling" do
    it "raises RubyGemsAPIError for 500 Internal Server Error" do
      server_error = Net::HTTPInternalServerError.new("1.0", "500", "Internal Server Error")
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { server_error }

      expect { gem_verifier.get_gem_info("rails") }.to raise_error(Rubysmithing::GemVerifier::RubyGemsAPIError) do |error|
        expect(error.status_code).to eq(500)
      end
    end

    it "raises RubyGemsAPIError for 502 Bad Gateway" do
      bad_gateway = Net::HTTPBadGateway.new("1.0", "502", "Bad Gateway")
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { bad_gateway }

      expect { gem_verifier.get_gem_info("rails") }.to raise_error(Rubysmithing::GemVerifier::RubyGemsAPIError) do |error|
        expect(error.status_code).to eq(502)
      end
    end

    it "raises RubyGemsAPIError for 503 Service Unavailable" do
      service_unavailable = Net::HTTPServiceUnavailable.new("1.0", "503", "Service Unavailable")
      allow(fake_http).to receive(:start).and_yield(fake_http)
      allow(fake_http).to receive(:open_timeout=)
      allow(fake_http).to receive(:read_timeout=)
      allow(fake_http).to receive(:request) { service_unavailable }

      expect { gem_verifier.get_gem_info("rails") }.to raise_error(Rubysmithing::GemVerifier::RubyGemsAPIError) do |error|
        expect(error.status_code).to eq(503)
      end
    end
  end
end