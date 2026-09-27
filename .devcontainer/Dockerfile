FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

# The base image's stale Yarn APT source can prevent the SSH feature from
# installing. SSH is needed only for `gh codespace ssh` verification.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && rm -rf /var/lib/apt/lists/*
