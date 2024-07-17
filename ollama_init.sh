# mkdir -p /usr/share/keyrings
# touch /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
#   && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
#     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
#     tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
# apt-get update
# apt-get install -y nvidia-container-toolkit

# # Configure NVIDIA Container Toolkit
# nvidia-ctk runtime configure --runtime=docker
# systemctl restart docker

# Test GPU integration
# docker run --gpus all nvidia/cuda:11.5.2-base-ubuntu20.04 nvidia-smi

docker compose -f ollama/docker-compose.yml up -d --build