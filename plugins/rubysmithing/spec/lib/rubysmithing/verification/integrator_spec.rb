# frozen_string_literal: true

require_relative "../../../../lib/rubysmithing/verification/integrator"
require_relative "../../../../spec_helper"

RSpec.describe Rubysmithing::Verification::Integrator do
  let(:gem_verifier) { instance_double("Rubysmithing::GemVerifier") }
  let(:context_cache) { instance_double("Rubysmithing::ContextCache") }
  let(:integrator) { described_class.new(gem_verifier: gem_verifier, context_cache: context_cache) }

  describe "#verify" do
    context "when gem exists on RubyGems.org" do
      let(:gem_info) do
        {
          name: "rails",
          version: "7.1.3.2",
          description: "Ruby on Rails framework"
        }
      end

      before do
        allow(gem_verifier).to receive(:verify_exists?).with("rails").and_return(true)
        allow(gem_verifier).to receive(:get_gem_info).with("rails").and_return(gem_info)
      end

      it "returns verified status" do
        result = integrator.verify("rails")
        expect(result.status).to eq(:verified)
        expect(result.gem_info).to eq(gem_info)
        expect(result.error).to be_nil
        expect(result.suggestions).to be_nil
      end
    end

    context "when gem exists with version constraint" do
      let(:gem_info) do
        { name: "rails", version: "7.0.0" }
      end

      before do
        allow(gem_verifier).to receive(:version_exists?).with("rails", "~> 7.0").and_return(true)
        allow(gem_verifier).to receive(:get_gem_info).with("rails").and_return(gem_info)
      end

      it "returns verified status" do
        result = integrator.verify("rails", "~> 7.0")
        expect(result.status).to eq(:verified)
        expect(result.gem_info[:version]).to eq("7.0.0")
      end
    end

    context "when gem does not exist" do
      before do
        allow(gem_verifier).to receive(:verify_exists?).with("nonexistent_gem").and_return(false)
      end

      it "returns not_found status with suggestions" do
        result = integrator.verify("nonexistent_gem")
        expect(result.status).to eq(:not_found)
        expect(result.gem_info).to be_nil
        expect(result.error).to include("not found on RubyGems.org")
        expect(result.suggestions).to be_an(Array)
      end
    end

    context "when gem version constraint cannot be satisfied" do
      before do
        allow(gem_verifier).to receive(:version_exists?)
          .with("colorize", "~> 1.0")
          .and_raise(Rubysmithing::GemVerifier::GemVersionNotFound.new("colorize", "~> 1.0", "reason"))
        allow(gem_verifier).to receive(:get_versions)
          .with("colorize")
          .and_return(["0.8.0", "0.8.1"])
      end

      it "returns unverified status with version info" do
        result = integrator.verify("colorize", "~> 1.0")
        expect(result.status).to eq(:unverified)
        expect(result.error).to include("version constraint")
        expect(result.error).to include("cannot be satisfied")
        expect(result.error).to include("Available versions")
        expect(result.error).to include("Latest:")
      end
    end

    context "when RubyGems.org is unavailable (DegradedError)" do
      before do
        allow(gem_verifier).to receive(:verify_exists?)
          .and_raise(Rubysmithing::GemVerifier::DegradedError.new(Net::OpenTimeout.new("timeout")))
      end

      context "when stale cache entry exists" do
        let(:cached_entry) do
          {
            gem_name: "rails",
            context7_id: "/rails/rails",
            method_sigs: ["method1", "method2"],
            stale: true,
            age_days: 10.0
          }
        end

        before do
          allow(context_cache).to receive(:fetch_stale).with("rails").and_return(cached_entry)
          allow(context_cache).to receive(:staleness_warning)
            .with("rails", entry: cached_entry)
            .and_return("# [WARNING: Stale API Syntax]\n# Cache is stale")
        end

        it "returns stale_fallback status" do
          result = integrator.verify("rails")
          expect(result.status).to eq(:stale_fallback)
          expect(result.gem_info).to eq(cached_entry)
          expect(result.staleness_warning).to include("Stale API Syntax")
        end
      end

      context "when no cache entry exists" do
        before do
          allow(context_cache).to receive(:fetch_stale).with("rails").and_return(nil)
        end

        it "returns unverified status with error" do
          result = integrator.verify("rails")
          expect(result.status).to eq(:unverified)
          expect(result.error).to include("RubyGems.org unavailable")
          expect(result.error).to include("no cached data")
        end
      end
    end

    context "when gem raises GemNotFound exception" do
      before do
        allow(gem_verifier).to receive(:verify_exists?)
          .and_raise(Rubysmithing::GemVerifier::GemNotFound.new("unknown_gem"))
      end

      it "returns not_found status with suggestions" do
        result = integrator.verify("unknown_gem")
        expect(result.status).to eq(:not_found)
        expect(result.error).to include("not found on RubyGems.org")
      end
    end
  end

  describe VerificationResult do
    describe "#verified?" do
      it "returns true for :verified status" do
        result = VerificationResult.new(status: :verified)
        expect(result.verified?).to be true
      end

      it "returns false for other statuses" do
        result = VerificationResult.new(status: :stale_fallback)
        expect(result.verified?).to be false
      end
    end

    describe "#stale_fallback?" do
      it "returns true for :stale_fallback status" do
        result = VerificationResult.new(status: :stale_fallback)
        expect(result.stale_fallback?).to be true
      end
    end

    describe "#not_found?" do
      it "returns true for :not_found status" do
        result = VerificationResult.new(status: :not_found)
        expect(result.not_found?).to be true
      end
    end
  end
end