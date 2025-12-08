#!/bin/bash
#
# quick-fix-deploy-env.sh
# Quick fix for missing .deploy.env on VM
#
# Usage on DEV VM:
#   cd ~/snippetly
#   bash scripts/quick-fix-deploy-env.sh <acr-server> <image-tag>
#
# Example:
#   bash scripts/quick-fix-deploy-env.sh snippetlyacr.azurecr.io latest
#

set -euo pipefail

ACR_SERVER="${1:-}"
IMAGE_TAG="${2:-latest}"

if [ -z "$ACR_SERVER" ]; then
  echo "Usage: $0 <acr-server> [image-tag]"
  echo ""
  echo "Example:"
  echo "  $0 snippetlyacr.azurecr.io latest"
  echo "  $0 snippetlyacr.azurecr.io abc123def"
  echo ""
  echo "To find your ACR server:"
  echo "  terraform output acr_login_server"
  echo "  OR check Azure Portal → Container Registry"
  exit 1
fi

echo "Creating .deploy.env..."
cat > .deploy.env << EOF
BACKEND_IMAGE=${ACR_SERVER}/snippetly-backend:${IMAGE_TAG}
FRONTEND_IMAGE=${ACR_SERVER}/snippetly-frontend:${IMAGE_TAG}
EOF

echo "✅ Created .deploy.env:"
cat .deploy.env

echo ""
echo "Now you can run:"
echo "  docker compose -f docker-compose.yml -f docker-compose.override.yml up -d"
