FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git curl \
    && rm -rf /var/lib/apt/lists/*

# Install ESPHome
RUN pip3 install esphome
