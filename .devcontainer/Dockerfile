# GitAgent Development Container
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libyaml-dev \
    sqlite3 \
    libsqlite3-dev \
    jq \
    vim \
    nano \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Install Ruby via rbenv
RUN git clone https://github.com/rbenv/rbenv.git /usr/local/rbenv \
    && git clone https://github.com/rbenv/ruby-build.git /usr/local/rbenv/plugins/ruby-build \
    && /usr/local/rbenv/plugins/ruby-build/install.sh
ENV PATH="/usr/local/rbenv/bin:/usr/local/rbenv/shims:${PATH}"

# Install Ruby 3.4.4
RUN rbenv install 3.4.4 && rbenv global 3.4.4

# Install Python 3.11
RUN apt-get update && apt-get install -y python3.11 python3.11-dev python3.11-venv python3-pip
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Set up workspace
WORKDIR /workspace

# Create vscode user
RUN useradd -m vscode && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER vscode

# Set up user environment
RUN echo 'export PATH="/usr/local/rbenv/bin:/usr/local/rbenv/shims:${PATH}"' >> ~/.bashrc
RUN echo 'eval "$(rbenv init -)"' >> ~/.bashrc

# Keep container running
CMD ["sleep", "infinity"]