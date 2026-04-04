#!/bin/bash
set -e

echo "🚀 Setting up GitAgent development environment..."

# Update package lists
sudo apt-get update

# Install additional system dependencies
sudo apt-get install -y \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libyaml-dev \
    sqlite3 \
    libsqlite3-dev \
    jq

# Install GitAgent CLI (if available)
echo "📦 Installing GitAgent CLI..."
if command -v npm &> /dev/null; then
    # Try to install gitagent globally (assuming it's available via npm)
    npm install -g gitagent || echo "⚠️ GitAgent CLI not available via npm, skipping..."
else
    echo "⚠️ npm not available, skipping GitAgent CLI installation"
fi

# Install Python testing dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user \
    pytest \
    pytest-cov \
    pytest-xdist \
    pyyaml \
    requests \
    black \
    flake8 \
    mypy

# Install Ruby testing dependencies
echo "💎 Installing Ruby dependencies..."
gem install \
    rspec \
    rubocop \
    bundler \
    yard

# Create scripts directory
mkdir -p /workspace/scripts
mkdir -p /workspace/tests
mkdir -p /workspace/docs

# Set up Python path
export PYTHONPATH="/workspace:${PYTHONPATH}"
echo 'export PYTHONPATH="/workspace:${PYTHONPATH}"' >> ~/.bashrc

# Set up aliases for common commands
echo 'alias validate="python3 /workspace/scripts/validate-migration.py"' >> ~/.bashrc
echo 'alias test-skills="python3 /workspace/scripts/test-skills.py"' >> ~/.bashrc
echo 'alias test-tools="python3 /workspace/scripts/test-tools.py"' >> ~/.bashrc

# Make the script executable
chmod +x /workspace/scripts/*.py 2>/dev/null || true

echo "✅ GitAgent development environment setup complete!"
echo ""
echo "Available commands:"
echo "  validate      - Run GitAgent migration validation"
echo "  test-skills   - Test all 25 skills"
echo "  test-tools    - Test custom tools"
echo "  pytest        - Run Python test suite"
echo "  gitagent      - GitAgent CLI (if available)"
echo ""
echo "Next steps:"
echo "1. Run 'validate' to check GitAgent migration"
echo "2. Run 'test-skills' to validate skill functionality"
echo "3. Run 'pytest tests/' to run full test suite"