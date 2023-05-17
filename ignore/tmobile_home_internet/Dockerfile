# https://www.feval.ca/posts/multistage-docker/
# https://medium.com/capital-one-tech/multi-stage-builds-and-dockerfile-b5866d9e2f84

# Build Stage
# Pull the base image
FROM python:3.10-slim-buster as base
# Set working directory
WORKDIR /app
# Install package manager
RUN pip install pipenv
# Install dependencies in project directory
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install

# Development Stage
FROM base as development
# Copy files from host to image
COPY . .
# Install dev dependencies
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

# Gets Sonarqube Scanner from Dockerhub and runs it
# FROM newtmitch/sonar-scanner:latest as sonarqube
# WORKDIR /app
# COPY --from=development /app .

# Unit Testing Stage
FROM development as unit_testing
# Run tests
RUN pipenv run pytest

# Integration Testing Stage
FROM development as integration_testing
# Run integration tests
RUN pipenv run 

# Linting Stage
FROM development as linting
# Run linting
RUN pipenv run flake8

# Runtime Stage
From base as run

EXPOSE 80