#!/bin/bash

# Check if a parameter is passed
if [ -z "$1" ]; then
  echo "Usage: $0 <up|down>"
  exit 1
fi

# Run the appropriate docker compose command based on the parameter
if [ "$1" == "up" ]; then
    ./chroma_init.sh up
    ./ollama_init.sh up
    ./aelfgpt_init.sh up
elif [ "$1" == "down" ]; then
    ./chroma_init.sh down
    ./ollama_init.sh down
    ./aelfgpt_init.sh down
else
  echo "Invalid parameter. Use 'up' or 'down'."
  exit 1
fi