#!/bin/bash

# Check if a parameter is passed
if [ -z "$1" ]; then
  echo "Usage: $0 <up|down>"
  exit 1
fi

# Run the appropriate docker compose command based on the parameter
if [ "$1" == "up" ]; then
  # curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  #   && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  #     sudo sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  #     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  # sudo apt-get update
  # sudo apt-get install -y nvidia-container-toolkit

  # Configure NVIDIA Container Toolkit
  # sudo nvidia-ctk runtime configure --runtime=docker
  # sudo service docker restart

  # Test GPU integration
  # docker run --gpus all nvidia/cuda:11.5.2-base-ubuntu20.04 nvidia-smi

  docker compose -f ollama/docker-compose.yml up -d --build
  docker exec -it ollama ollama run gemma2:27b
elif [ "$1" == "down" ]; then
  docker compose -f ollama/docker-compose.yml down
else
  echo "Invalid parameter. Use 'up' or 'down'."
  exit 1
fi