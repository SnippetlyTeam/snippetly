# Snippetly Infrastructure on Microsoft Azure

## Overview
- Application: FastAPI backend + React/Vite SPA frontend, with PostgreSQL, Redis, MongoDB, and Celery (worker + beat).
- Infrastructure: two Azure Linux VMs (dev and prod) running Docker Compose, created by a single Terraform apply.
- Networking:
  - **DEV**: HTTP on port 80 (+ optional ports 8000, 5173 for debugging); SSH on port 22
  - **PROD**: HTTPS on port 443 with Let's Encrypt; HTTP port 80 for ACME challenge + redirect; SSH on port 22
- Data durability: host‑path persistent storage on each VM and backups to Azure Blob Storage (per‑environment containers).
- Delivery: Two GitHub Actions workflows:
  - `ci-cd-dev.yml`: deploys from `develop` branch to DEV
  - `ci-cd-prod.yml`: deploys from `main` branch to PROD
  - Images stored in Azure Container Registry (ACR).

This document explains how the infrastructure is designed and how all pieces fit together.

## Architecture diagram (text)

**DEV Environment:**
- User → HTTP:80 → Nginx (frontend container)
  - Serves SPA static files
  - Proxies `/api/*` → `backend:8000` (internal Docker network)
- Optional direct access: User → HTTP:8000 → backend (if allow_dev_ports enabled)

**PROD Environment:**
- User → HTTPS:443 → Nginx reverse proxy (nginx-proxy container)
  - TLS termination with Let's Encrypt certificates
  - Proxies all traffic → `frontend:80` (internal)
- User → HTTP:80 → Nginx reverse proxy
  - Serves ACME challenge for Let's Encrypt
  - Redirects all other traffic → HTTPS:443
- Frontend (Nginx) → internally serves SPA and proxies `/api/*` → `backend:8000`

**Common (both environments):**
- Backend (FastAPI, `uvicorn` workers) → talks to:
  - PostgreSQL (internal)
  - Redis (internal)
  - MongoDB (internal)
  - Azure Blob Storage (SDK) for file uploads and backups
- Celery worker and Celery beat (internal)
- Azure resources around the VMs:
  - VNet + Subnet + NSG (open: 22/80/443, optional 8000/5173 for dev)
  - Azure Container Registry (ACR) for container images
  - Storage Account with per‑environment containers for media and backups
- Infrastructure as Code: Terraform in `infra/terraform`

## Azure resources (Terraform)
Terraform provisions in one apply:
- VNet + Subnet (shared)
- Network Security Group (NSG)
  - Ingress 22/TCP (SSH) - always open
  - Ingress 80/TCP (HTTP) - always open
  - Ingress 443/TCP (HTTPS) - always open (for production TLS)
  - Ingress 8000/TCP, 5173/TCP - conditionally open if `allow_dev_ports=true` (dev debugging)
- Linux VMs: one for dev, one for prod
  - Each runs Docker + Compose
  - cloud‑init initializes each host:
    - Installs Docker + Compose plugin
    - Clones repo to `~/snippetly`
    - Creates data dirs: `/opt/app-data/{postgres,redis,mongo,certbot/conf,certbot/www}`
    - Prepares `~/snippetly/.deploy.env`
    - Installs cron jobs for automatic DB migrations (@reboot and periodic) and optional nightly backups
- Azure Storage Account
  - Media containers: dev and prod
  - Backup containers: dev and prod
- Azure Container Registry (ACR)

## Compute & application layer (Docker Compose)

**Base stack** (`docker-compose.yml`) defines core services used by both environments:

- frontend (Nginx; serves SPA built by Vite)
  - Base config: `expose: 80` (internal only in prod), `ports: 80:80` (published in dev via override)
  - Role: serves SPA static files, proxies `/api/*` to `backend:8000`
  - Restart policy: `unless-stopped`

- backend (FastAPI)
  - Command: `uv run uvicorn src.main:app ... --port 8000 --workers 2`
  - Ports: `expose: 8000` (internal only)
  - Depends on: `db`, `redis`, `mongodb`
  - Volumes: mounts `./backend/static/avatars` for media
  - Healthcheck: `curl -fsS http://localhost:8000/api/health`
  - Restart: `unless-stopped`

- db (PostgreSQL)
  - Ports: none published
  - Volume: `/opt/app-data/postgres:/var/lib/postgresql/data`
  - Healthcheck: `pg_isready`
  - Restart: `unless-stopped`

- redis
  - Ports: none published
  - Volume: `/opt/app-data/redis:/data`
  - Healthcheck: `redis-cli ping`
  - Restart: `unless-stopped`

- mongodb
  - Ports: none published
  - Volume: `/opt/app-data/mongo:/data/db`
  - Healthcheck: `mongosh ... db.adminCommand('ping')`
  - Restart: `unless-stopped`

- celery-worker
  - Command: `uv run celery -A src.worker.app.app worker --loglevel=info`
  - Depends on: `db`, `redis`
  - Restart: `unless-stopped`

- celery-beat
  - Command: `uv run celery -A src.worker.app.app beat --loglevel=info`
  - Depends on: `db`, `redis`
  - Restart: `unless-stopped`

- migrate (one‑off)
  - Command: `uv run alembic upgrade head`
  - Depends on: `db`
  - Restart: `"no"`

**Environment-specific overlays:**

**DEV** (`docker-compose.override.yml`):
- Exposes additional ports for debugging:
  - db: `5432:5432`
  - redis: `6379:6379`
  - mongodb: `27017:27017`
  - backend: `8000:8000`
- Adds `pgadmin` service on port `9090:80`
- Frontend publishes `80:80` to host

**PROD** (`docker-compose.prod.yml`):
- Removes public port from frontend (keeps it internal)
- Adds `nginx-proxy` service:
  - Publishes `80:80` and `443:443`
  - TLS termination with Let's Encrypt certificates
  - Proxies all traffic to `frontend:80`
  - Serves ACME challenge on port 80
  - Redirects HTTP → HTTPS
- Adds `certbot` service:
  - Manages Let's Encrypt certificates
  - Runs renewal checks twice daily
  - Auto-reloads nginx on successful renewal

Important: In dev, multiple ports are exposed for debugging. In prod, only nginx-proxy exposes ports 80/443; all app containers are internal-only.

## Networking & security

**DEV Environment:**
- NSG rules: 22 (SSH), 80 (HTTP), optionally 8000/5173 (if `allow_dev_ports=true`)
- HTTP-only (no TLS) for simplicity
- Direct access to backend/databases possible if dev ports enabled
- Access via IP address: http://172.201.5.167

**PROD Environment:**
- NSG rules: 22 (SSH), 80 (HTTP - ACME + redirect only), 443 (HTTPS - all user traffic)
- HTTPS-only for user traffic via Let's Encrypt
- All application containers (backend, DB, Redis, MongoDB, Celery) are internal-only
- Access via domain: https://snippetly.codes
- TLS certificates auto-renew 30 days before expiration

**Common:**
- Backend, PostgreSQL, Redis, MongoDB, Celery communicate only on internal Docker network
- GitHub Actions authenticates via SSH to perform deploy steps on VMs
- No public access to databases or internal services (except dev debugging ports)

## Persistent storage
Cloud‑init creates host directories on the VM for persistent data:
- PostgreSQL: `/opt/app-data/postgres` → container `/var/lib/postgresql/data`
- Redis: `/opt/app-data/redis` → container `/data`
- MongoDB: `/opt/app-data/mongo` → container `/data/db`
- Let's Encrypt certificates (PROD only):
  - `/opt/app-data/certbot/conf` → nginx-proxy `/etc/letsencrypt`
  - `/opt/app-data/certbot/www` → certbot `/var/www/certbot`

These directories survive container restarts and most VM reboots, providing basic durability.

## Backups
- Scripts on the VM:
  - `scripts/backup_pg.sh`: runs `pg_dump` inside `db`, copies dump out, then invokes `backend/ops/upload_to_azure.py` to push to Azure Blob
  - `scripts/backup_mongo.sh`: runs `mongodump` inside `mongodb`, copies archive out, then uploads via the same helper
- Upload prefixes in Blob Storage:
  - `backups/postgres/`
  - `backups/mongo/`
- Container selection:
  - Terraform variables create and output per‑environment backup containers
  - Backend `.env` can set `AZURE_BACKUP_CONTAINER` (else uses media container)
- This is a simple, real backup flow. See restore steps in `readme-deploy.md`.

## Environment variables & secrets overview
- Terraform inputs (tfvars):
  - `location`, `resource_group_name`, `ssh_public_key`, `vm_size`, `admin_username`
  - `vnet_cidr`, `subnet_cidr`, `allow_dev_ports`
  - `repo_url`, `backend_env_content_dev`, `backend_env_content_prod`
  - `storage_account_name`, `media_container_dev`, `media_container_prod`, `backup_container_dev`, `backup_container_prod`
  - `acr_name`
- VM / application (backend `.env`):
  - DB settings: `POSTGRES_*`
  - Redis: `REDIS_*`
  - MongoDB: `MONGO_*`, `MONGODB_*`, `MONGO_INITDB_*`
  - Security/app: `SECRET_KEY_*`, `ENVIRONMENT`, `FRONTEND_URL`, optional email/OAuth settings
  - Azure Blob Storage: `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_ACCOUNT_KEY` or `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_BLOB_ENDPOINT` (optional), `AZURE_MEDIA_CONTAINER`, `AZURE_BACKUP_CONTAINER`
- GitHub Actions secrets (per environment):
  - ACR (Service Principal): `<ENV>_ACR_LOGIN_SERVER`, `<ENV>_AZURE_SP_APP_ID`, `<ENV>_AZURE_SP_PASSWORD`
  - SSH: `<ENV>_SSH_HOST`, `<ENV>_SSH_USER`, `<ENV>_SSH_KEY`
  - Optional smoke tests URL: `<ENV>_PUBLIC_URL` (else falls back to `http://<SSH_HOST>`)

## CI/CD flow (GitHub Actions + ACR)

**Branching Model:**
- `develop` branch → DEV environment
- `main` branch → PROD environment

**Workflows:**

- `.github/workflows/ci-cd-dev.yml`
  - **Triggers:**
    - CI: PRs to `develop` → backend tests (pytest, ruff, pyright) + frontend build (no deploy)
    - CD: Push to `develop` → full CI + build images + deploy to DEV
  - **Image tags:** `<commit_sha>` (e.g., `snippetly-backend:a1b2c3d`)
  - **Deploy command:** `docker compose -f docker-compose.yml -f docker-compose.override.yml up -d`
  - **Concurrency:** Only one dev deployment at a time (in‑progress runs are canceled)

- `.github/workflows/ci-cd-prod.yml`
  - **Triggers:**
    - CD: Push to `main` → full CI + build images + deploy to PROD
  - **Image tags:** `<commit_sha>` and `latest` (e.g., `snippetly-backend:a1b2c3d` and `snippetly-backend:latest`)
  - **Deploy command:** `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
  - **Concurrency:** Only one prod deployment at a time (in‑progress runs are NOT canceled for safety)
  - **HTTPS:** Production deployment maintains HTTPS via nginx-proxy + certbot services

**Common:**
- Images are pushed to Azure Container Registry (ACR)
- Deployment updates `~/snippetly/.deploy.env` on the VM with image tags
- Migrations are handled by cron on the VMs (not run from CI/CD)
- Each workflow uses environment-specific secrets for ACR and SSH access

## Health checks & monitoring basics
- Backend endpoint: `GET /api/health` returns `{ "status": "ok" }`
- Docker healthchecks:
  - backend: `curl http://localhost:8000/api/health`
  - db: `pg_isready`
  - redis: `redis-cli ping`
  - mongodb: `mongosh db.adminCommand('ping')`
- CI smoke tests: `curl -fsS http://<host>/api/health` and fetch SPA root
- Recommended (out of scope here): basic Azure Monitor alerts for CPU, memory, and disk

## Future improvements (optional)
- Add TLS/HTTPS via Azure Load Balancer/Application Gateway or Nginx + certbot (not part of current setup)
- Managed database services for higher availability
- Centralized logging (Azure Monitor Agent + Log Analytics), dashboards/alerts
- Potential migration to AKS if service count/scale grows (not in current scope)

