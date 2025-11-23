# Snippetly Infrastructure on Microsoft Azure

## Overview
- Application: FastAPI backend + React/Vite SPA frontend, with PostgreSQL, Redis, MongoDB, and Celery (worker + beat).
- Infrastructure: two Azure Linux VMs (dev and prod) running Docker Compose, created by a single Terraform apply.
- Networking: HTTP‑only on port 80; SSH on port 22. No TLS/HTTPS.
- Data durability: host‑path persistent storage on each VM and backups to Azure Blob Storage (per‑environment containers).
- Delivery: Two GitHub Actions workflows — `ci-cd-dev.yml` (CI on PRs + Dev CD on branch push) and `ci-cd-prod.yml` (Prod CD on tags). Images stored in Azure Container Registry (ACR).

This document explains how the infrastructure is designed and how all pieces fit together.

## Architecture diagram (text)
- User → HTTP:80 → Nginx (frontend container)
  - Serves SPA static files
  - Proxies `/api/*` → `backend:8000` (internal Docker network)
- Backend (FastAPI, `uvicorn` workers) → talks to:
  - PostgreSQL (internal)
  - Redis (internal)
  - MongoDB (internal)
  - Azure Blob Storage (SDK) for file uploads and backups
- Celery worker and Celery beat (internal)
- Azure resources around the VMs:
  - VNet + Subnet + NSG (open: 22/80)
  - Azure Container Registry (ACR) for container images
  - Storage Account with per‑environment containers for media and backups
- Infrastructure as Code: Terraform in `infra/terraform`

## Azure resources (Terraform)
Terraform provisions in one apply:
- VNet + Subnet (shared)
- Network Security Group (NSG)
  - Ingress 22/TCP (SSH)
  - Ingress 80/TCP (HTTP)
  - No HTTPS/443 (by design)
- Linux VMs: one for dev, one for prod
  - Each runs Docker + Compose
  - cloud‑init initializes each host (installs Docker, clones repo, creates data dirs, prepares `/opt/snippetly/.deploy.env`)
  - cloud‑init also installs cron jobs for automatic DB migrations (@reboot and periodic) and optional nightly backups
- Azure Storage Account
  - Media containers: dev and prod
  - Backup containers: dev and prod
- Azure Container Registry (ACR)

## Compute & application layer (Docker Compose)
On the VM, Docker Compose defines the following services (single compose file `docker-compose.yml` used on servers):

- frontend (Nginx; single Dockerfile builds and serves via Nginx)
  - Ports: publishes `80:80` (the only public port)
  - Role: serves SPA, proxies `/api/*` to `backend:8000`
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

Important: the backend is not exposed publicly; only the frontend publishes port 80.

## Networking & security
- Only ports 22 (SSH) and 80 (HTTP) are open in the NSG.
- Backend, PostgreSQL, Redis, MongoDB, Celery are reachable only on the internal Docker network.
- HTTP‑only by design. No TLS/HTTPS.
- GitHub Actions authenticates via SSH to perform deploy steps on the VM.

## Persistent storage
Cloud‑init creates host directories on the VM for persistent data:
- PostgreSQL: `/opt/app-data/postgres` → container `/var/lib/postgresql/data`
- Redis: `/opt/app-data/redis` → container `/data`
- MongoDB: `/opt/app-data/mongo` → container `/data/db`

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
- `.github/workflows/ci-cd-dev.yml`
  - CI: runs on PRs to `main`/`develop`; backend tests (pytest) and frontend build
  - CD Dev: push to any non-`main` branch → build & push images → SSH deploy to dev → smoke tests
  - Concurrency: only one dev deployment at a time (in‑progress runs are canceled)
- `.github/workflows/ci-cd-prod.yml`
  - CD Prod: tags `v*` → build & push versioned images → SSH deploy to prod → smoke tests
  - Concurrency: only one prod deployment at a time (in‑progress runs are not canceled)
- Migrations: handled by cron on the VMs (not run from CI/CD)

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

