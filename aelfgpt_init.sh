#!/bin/bash

# Check if a parameter is passed
if [ -z "$1" ]; then
  echo "Usage: $0 <up|down>"
  exit 1
fi

# Change to the aelfgpt directory
cd aelfgpt

# Check if the chroma directory exists, if not, clone it
if [ ! -f ".env" ]; then
  cp example.env .env
fi

# Change back to the previous directory
cd -

# Run the appropriate docker compose command based on the parameter
if [ "$1" == "up" ]; then
  docker compose -f aelfgpt/docker-compose.yml up -d --build
elif [ "$1" == "down" ]; then
  docker compose -f aelfgpt/docker-compose.yml down
else
  echo "Invalid parameter. Use 'up' or 'down'."
  exit 1
fi
