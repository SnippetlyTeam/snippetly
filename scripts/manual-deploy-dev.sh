#!/bin/bash
#
# manual-deploy-dev.sh
# Manual deployment script for DEV VM when you want to deploy without CI/CD
#
# This script sets up .deploy.env with image tags and deploys the stack
#
# Usage on DEV VM:
#   cd ~/snippetly
#   bash scripts/manual-deploy-dev.sh
#

set -euo pipefail

echo "============================================"
echo "Manual DEV Deployment Script"
echo "============================================"
echo ""

# Check we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
  echo "❌ Error: docker-compose.yml not found"
  echo "Please run this script from ~/snippetly directory"
  exit 1
fi

# Get ACR login server from user or use default
read -p "Enter ACR login server (e.g., snippetlyacr.azurecr.io): " ACR_SERVER
ACR_SERVER=${ACR_SERVER:-snippetlyacr.azurecr.io}

# Get image tag from user or use 'latest'
read -p "Enter image tag to deploy [latest]: " IMAGE_TAG
IMAGE_TAG=${IMAGE_TAG:-latest}

echo ""
echo "Will deploy:"
echo "  Backend:  ${ACR_SERVER}/snippetly-backend:${IMAGE_TAG}"
echo "  Frontend: ${ACR_SERVER}/snippetly-frontend:${IMAGE_TAG}"
echo ""
read -p "Continue? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
  echo "Aborted."
  exit 0
fi

# Create .deploy.env
echo ""
echo "Creating .deploy.env..."
cat > .deploy.env << EOF
BACKEND_IMAGE=${ACR_SERVER}/snippetly-backend:${IMAGE_TAG}
FRONTEND_IMAGE=${ACR_SERVER}/snippetly-frontend:${IMAGE_TAG}
EOF

echo "✅ .deploy.env created:"
cat .deploy.env

# Check if backend/.env exists
echo ""
if [ ! -f backend/.env ]; then
  echo "⚠️  backend/.env not found"
  echo "Creating from sample..."
  cp backend/config_envs/.env.prod.sample backend/.env
  echo "✅ Created backend/.env from sample"
  echo "⚠️  IMPORTANT: Edit backend/.env with your actual values!"
  echo ""
  read -p "Press Enter to continue after you've edited backend/.env..."
fi

# Load .deploy.env
echo ""
echo "Loading deployment environment..."
set -a
source .deploy.env
set +a

echo "Using:"
echo "  BACKEND_IMAGE=$BACKEND_IMAGE"
echo "  FRONTEND_IMAGE=$FRONTEND_IMAGE"

# Login to ACR
echo ""
read -p "Do you need to login to ACR? (y/n) [y]: " NEED_LOGIN
NEED_LOGIN=${NEED_LOGIN:-y}

if [ "$NEED_LOGIN" = "y" ]; then
  echo "Logging into ACR..."
  echo "You can use Service Principal or Azure CLI:"
  echo "  1) Service Principal: docker login \$ACR_SERVER -u \$SP_ID -p \$SP_PASSWORD"
  echo "  2) Azure CLI: az acr login --name <registry-name>"
  echo ""
  read -p "Enter choice (1/2): " LOGIN_CHOICE

  if [ "$LOGIN_CHOICE" = "1" ]; then
    read -p "Service Principal App ID: " SP_ID
    read -sp "Service Principal Password: " SP_PASSWORD
    echo ""
    echo "$SP_PASSWORD" | docker login "$ACR_SERVER" -u "$SP_ID" --password-stdin
  else
    ACR_NAME=$(echo "$ACR_SERVER" | cut -d'.' -f1)
    az acr login --name "$ACR_NAME"
  fi
fi

# Pull images
echo ""
echo "Pulling Docker images..."
docker compose -f docker-compose.yml -f docker-compose.override.yml pull

# Start services
echo ""
echo "Starting services..."
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Wait for services
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Verify
echo ""
echo "Verifying deployment..."
docker compose -f docker-compose.yml -f docker-compose.override.yml ps

echo ""
echo "============================================"
echo "✅ Manual deployment completed!"
echo "============================================"
echo ""
echo "Access your app at: http://$(curl -s ifconfig.me)"
echo ""
echo "To check logs:"
echo "  docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f"
echo ""
echo "To stop:"
echo "  docker compose -f docker-compose.yml -f docker-compose.override.yml down"
echo ""
