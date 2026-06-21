# Multi-stage build: Stage 1 - Node.js builder for all-contributors CLI
FROM node:22-slim AS node-builder

# Install all-contributors-cli globally
RUN npm install -g all-contributors-cli

# Multi-stage build: Stage 2 - Python runtime
FROM python:3.14.6-slim

# Copy Node.js runtime and all-contributors CLI from builder stage
COPY --from=node-builder /usr/local/bin/node /usr/local/bin/node
COPY --from=node-builder /usr/local/lib/node_modules /usr/local/lib/node_modules

# Create symlink for all-contributors command
RUN ln -s /usr/local/lib/node_modules/all-contributors-cli/dist/cli.js /usr/local/bin/all-contributors && \
    chmod +x /usr/local/bin/all-contributors

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

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
