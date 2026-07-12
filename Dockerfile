# Stage 1: Install all-contributors-cli
FROM node:22-slim AS builder
RUN npm install -g all-contributors-cli

# Stage 2: Python runtime
FROM python:3.14.6-slim

# Copy node binary + all-contributors artifacts from builder
COPY --from=builder /usr/local/bin/node /usr/local/bin/node
COPY --from=builder /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/all-contributors-cli/dist/cli.js /usr/local/bin/all-contributors \
    && chmod +x /usr/local/bin/all-contributors

# Install git
RUN apt-get update \
  && apt-get install --yes --no-install-recommends git \
  && rm -rf /var/lib/apt/lists/*

# Create and set the 'app' working directory
RUN mkdir /app
WORKDIR /app

# Copy repository contents into the working directory
COPY . /app

# Update pip
RUN pip install -U pip

# Install package
RUN pip install .

# Set entrypoint
ENTRYPOINT ["all-all-contributors"]
