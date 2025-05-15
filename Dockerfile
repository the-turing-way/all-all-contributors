# Dockerfile copied from: 
# - https://github.com/sgibson91/bump-helm-deps-action/blob/main/Dockerfile

# Use a Python slim image
FROM python:3.13.3-slim

# Install gcc
# NOTE: Sarah can't remember why she needed this line... Let's see what breaks without it!
# RUN apt-get update && apt-get install --yes gcc

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
