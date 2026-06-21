# Dockerfile copied from:
# - https://github.com/sgibson91/bump-helm-deps-action/blob/main/Dockerfile

# Use a Python slim image
FROM python:3.14.6-slim

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
