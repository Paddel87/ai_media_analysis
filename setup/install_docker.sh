#!/bin/bash
# Install Docker & Docker Compose on a fresh VPS (Ubuntu/Debian)

echo "Updating system..."
apt update && apt upgrade -y

echo "Installing required packages..."
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

echo "Adding Docker GPG key and repository..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Installing Docker CE..."
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "Enabling Docker service..."
systemctl enable docker
systemctl start docker

echo "Testing Docker installation..."
docker --version && docker compose version

echo "Docker installation completed."
