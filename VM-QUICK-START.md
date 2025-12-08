# VM Quick Start Guide

## After SSH to VM

### 1. Navigate to project directory
```bash
cd ~/snippetly
```

### 2. Check current state
```bash
bash scripts/diagnose-vm-deploy.sh
```

This will verify:
- ✅ You're in the correct directory
- ✅ Docker Compose files exist
- ✅ `.deploy.env` is configured
- ✅ `backend/.env` exists
- ✅ Docker is running
- ✅ ACR login status

### 3. Quick fix if .deploy.env is missing

```bash
bash scripts/quick-fix-deploy-env.sh snippetlyacr.azurecr.io latest
```

### 4. Manual deployment (DEV)

```bash
bash scripts/manual-deploy-dev.sh
```

This interactive script will:
- Prompt for ACR server and image tag
- Create `.deploy.env`
- Ensure `backend/.env` exists
- Login to ACR (optional)
- Pull images
- Start services

### 5. Manual deployment (one-liner)

**DEV:**
```bash
cd ~/snippetly && \
cat > .deploy.env << 'EOF'
BACKEND_IMAGE=snippetlyacr.azurecr.io/snippetly-backend:latest
FRONTEND_IMAGE=snippetlyacr.azurecr.io/snippetly-frontend:latest
EOF
docker compose -f docker-compose.yml -f docker-compose.override.yml pull && \
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

**PROD:**
```bash
cd ~/snippetly && \
cat > .deploy.env << 'EOF'
BACKEND_IMAGE=snippetlyacr.azurecr.io/snippetly-backend:latest
FRONTEND_IMAGE=snippetlyacr.azurecr.io/snippetly-frontend:latest
EOF
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull && \
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 6. Check deployment status

```bash
docker compose ps
docker compose logs -f
```

### 7. HTTPS Setup (PROD only, one-time)

After initial deployment and DNS configuration:

```bash
cd ~/snippetly
sudo bash scripts/setup-https-prod.sh your-email@example.com
```

## Important Paths

- **Project directory**: `~/snippetly` (NOT `/opt/snippetly`)
- **Deployment env**: `~/snippetly/.deploy.env`
- **Backend env**: `~/snippetly/backend/.env`
- **Persistent data**: `/opt/app-data/{postgres,redis,mongo,certbot}`

## Common Issues

### Issue: "BACKEND_IMAGE variable is not set"
**Solution**: You're either in the wrong directory or `.deploy.env` is missing
```bash
cd ~/snippetly
bash scripts/quick-fix-deploy-env.sh snippetlyacr.azurecr.io latest
```

### Issue: "Cannot pull from ACR"
**Solution**: Login to ACR
```bash
az acr login --name snippetlyacr
# OR
docker login snippetlyacr.azurecr.io -u <SP_ID> -p <SP_PASSWORD>
```

### Issue: Services fail to start
**Solution**: Check logs and ensure backend/.env is configured
```bash
docker compose logs backend
docker compose logs db
```

## CI/CD Automated Deployment

The VMs are automatically deployed via GitHub Actions:

- **DEV VM**: Push to `develop` branch
- **PROD VM**: Push to `main` branch

GitHub Actions will:
1. Build and push Docker images to ACR
2. SSH to the VM
3. Navigate to `~/snippetly`
4. Update `.deploy.env` with new image tags
5. Pull latest code from git
6. Pull Docker images
7. Restart services with `docker compose up -d`

No manual intervention needed after the initial setup!
