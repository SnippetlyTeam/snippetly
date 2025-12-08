#!/bin/bash
#
# diagnose-vm-deploy.sh
# Diagnostic script to check VM deployment readiness
#
# Run this on the VM to verify everything is configured correctly
# before attempting deployment
#
# Usage:
#   cd ~/snippetly
#   bash scripts/diagnose-vm-deploy.sh
#

set -euo pipefail

echo "============================================"
echo "Snippetly VM Deployment Diagnostics"
echo "============================================"
echo ""

# Check current directory
echo "1. Current Directory Check"
echo "   Current: $(pwd)"
EXPECTED_DIR="$HOME/snippetly"
if [ "$(pwd)" = "$EXPECTED_DIR" ] || [ "$(basename $(pwd))" = "snippetly" ]; then
  echo "   ✅ Correct directory"
else
  echo "   ❌ WRONG DIRECTORY! Should be ~/snippetly"
  echo "   Run: cd ~/snippetly"
  exit 1
fi
echo ""

# Check if docker-compose.yml exists
echo "2. Docker Compose Files Check"
if [ -f "docker-compose.yml" ]; then
  echo "   ✅ docker-compose.yml exists"
else
  echo "   ❌ docker-compose.yml NOT FOUND"
  exit 1
fi

if [ -f "docker-compose.override.yml" ]; then
  echo "   ✅ docker-compose.override.yml exists (DEV)"
elif [ -f "docker-compose.prod.yml" ]; then
  echo "   ✅ docker-compose.prod.yml exists (PROD)"
else
  echo "   ❌ No environment overlay found"
  exit 1
fi
echo ""

# Check .deploy.env
echo "3. Deployment Environment (.deploy.env)"
if [ -f ".deploy.env" ]; then
  echo "   ✅ .deploy.env exists"
  echo "   Contents:"
  cat .deploy.env | sed 's/^/      /'

  # Check if variables are set
  source .deploy.env
  if [ -z "$BACKEND_IMAGE" ] || [ -z "$FRONTEND_IMAGE" ]; then
    echo "   ❌ Variables are empty!"
  else
    echo "   ✅ Variables are set"
  fi
else
  echo "   ❌ .deploy.env NOT FOUND"
  echo ""
  echo "   Create it with:"
  echo "   cat > .deploy.env << 'EOF'"
  echo "BACKEND_IMAGE=snippetlyacr.azurecr.io/snippetly-backend:latest"
  echo "FRONTEND_IMAGE=snippetlyacr.azurecr.io/snippetly-frontend:latest"
  echo "EOF"
  exit 1
fi
echo ""

# Check backend/.env
echo "4. Backend Environment (backend/.env)"
if [ -f "backend/.env" ]; then
  echo "   ✅ backend/.env exists"
  echo "   First 10 lines (secrets hidden):"
  head -10 backend/.env | sed 's/=.*/=***/' | sed 's/^/      /'
else
  echo "   ❌ backend/.env NOT FOUND"
  echo ""
  echo "   Create from sample:"
  echo "   cp backend/config_envs/.env.prod.sample backend/.env"
  echo "   vim backend/.env  # Edit with actual values"
  exit 1
fi
echo ""

# Check Docker is running
echo "5. Docker Service Check"
if docker info &> /dev/null; then
  echo "   ✅ Docker is running"
else
  echo "   ❌ Docker is not running or not accessible"
  echo "   Try: sudo systemctl start docker"
  exit 1
fi
echo ""

# Check ACR login
echo "6. ACR Login Check"
source .deploy.env
ACR_SERVER=$(echo "$BACKEND_IMAGE" | cut -d'/' -f1)
echo "   ACR Server: $ACR_SERVER"

if docker pull "$BACKEND_IMAGE" &> /dev/null; then
  echo "   ✅ Can pull from ACR (already logged in)"
else
  echo "   ⚠️  Cannot pull from ACR - may need to login"
  echo ""
  echo "   Login with:"
  echo "   az acr login --name ${ACR_SERVER%%.*}"
  echo "   OR"
  echo "   docker login $ACR_SERVER -u <SP_ID> -p <SP_PASSWORD>"
fi
echo ""

# Check data directories
echo "7. Persistent Data Directories"
for dir in /opt/app-data/postgres /opt/app-data/redis /opt/app-data/mongo; do
  if [ -d "$dir" ]; then
    echo "   ✅ $dir exists"
  else
    echo "   ⚠️  $dir missing (will be created automatically)"
  fi
done

# Check certbot directories for PROD
if [ -f "docker-compose.prod.yml" ]; then
  for dir in /opt/app-data/certbot/conf /opt/app-data/certbot/www; do
    if [ -d "$dir" ]; then
      echo "   ✅ $dir exists"
    else
      echo "   ⚠️  $dir missing (needed for HTTPS)"
    fi
  done
fi
echo ""

# Check git branch
echo "8. Git Branch"
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "   Current branch: $BRANCH"
if [ -f "docker-compose.override.yml" ]; then
  if [ "$BRANCH" = "develop" ]; then
    echo "   ✅ Correct branch for DEV"
  else
    echo "   ⚠️  DEV VM should be on 'develop' branch"
  fi
elif [ -f "docker-compose.prod.yml" ]; then
  if [ "$BRANCH" = "main" ]; then
    echo "   ✅ Correct branch for PROD"
  else
    echo "   ⚠️  PROD VM should be on 'main' branch"
  fi
fi
echo ""

echo "============================================"
echo "Diagnostics Complete!"
echo "============================================"
echo ""

# Suggest next steps
if [ -f "docker-compose.override.yml" ]; then
  echo "Ready to deploy DEV with:"
  echo "  docker compose -f docker-compose.yml -f docker-compose.override.yml pull"
  echo "  docker compose -f docker-compose.yml -f docker-compose.override.yml up -d"
elif [ -f "docker-compose.prod.yml" ]; then
  echo "Ready to deploy PROD with:"
  echo "  docker compose -f docker-compose.yml -f docker-compose.prod.yml pull"
  echo "  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
fi
echo ""
