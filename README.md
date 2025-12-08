# Snippetly

Snippetly is a platform for creating and sharing code snippets. It consists of a FastAPI backend and a React (Vite) frontend, with PostgreSQL, Redis, MongoDB, and Celery (worker/beat).

This repository includes everything to provision and operate two environments (dev and prod) on Microsoft Azure using a single VM per environment with Docker Compose, HTTP-only (port 80), persistent storage, backups to Azure Blob Storage, and CI/CD via two workflows (ACR with Service Principal).

---

## What you get

- Two environments (dev and prod) created by a single `terraform apply`.
- Single VM per environment, Docker Compose runtime.
- HTTP-only on port 80 via Nginx serving the SPA and proxying `/api` to the backend.
- Persistent host-path storage on the VM under `/opt/app-data/...`.
- Backups to Azure Blob Storage (per-environment containers) via scripts.
- Automatic DB migrations via cron on each VM (@reboot + periodic).
- Two GitHub Actions workflows for CI + CD (dev via non-main branch push, prod via version tags).

---

## Quickstart (from zero to running)

1) Clone the repo

```bash
git clone <your-fork-or-repo-url>
cd snippetly
```

2) Configure Terraform

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your Azure region, SSH key, storage account name, ACR name, etc.
terraform init
terraform apply
```

Terraform will create: Resource Group, VNet, Subnet, NSG (22/80), two Linux VMs (dev/prod), a Storage Account with containers (media + backups), and an Azure Container Registry (ACR). Both VMs are initialized by cloud-init (Docker, repo checkout, single compose, cron for migrations and backups).

3) Configure GitHub Actions secrets (dev/prod)

Set ACR Service Principal secrets and SSH (host/user/key), and optional PUBLIC_URL for smoke tests. See `readme-deploy.md` for the complete list.

4) Deploy

- Dev: push to any non-`main` branch to trigger build, push, and deploy to the dev VM.
- Prod: create a tag `vX.Y.Z` to build, push, and deploy to the prod VM.

After deploy, open:
- Dev: `http://<dev_vm_public_ip>/`
- Prod: `http://<prod_vm_public_ip>/`

Health endpoint: `http://<vm_ip>/api/health` returns `{ "status": "ok" }`.

---

## Migrations and Backups

- Migrations run automatically on each VM via cron (@reboot and every 10 minutes) using `docker compose run --rm migrate`.
- Backups: two scripts on the VM upload Postgres and MongoDB archives to the configured Object Storage backup bucket.
  - `~/snippetly/scripts/backup_pg.sh`
  - `~/snippetly/scripts/backup_mongo.sh`

Nightly cron entries are installed by cloud-init (can be disabled by removing entries on the VM).

---

## CI/CD

Two workflows in `.github/workflows/`:

- `ci-cd-dev.yml`
  - CI runs on PRs to `main`/`develop` (backend tests and frontend build).
  - CD Dev runs on pushes to any non-main branch.
- `ci-cd-prod.yml`
  - CD Prod runs on tags `v*`.

Each deploy updates `.deploy.env` on the VM, pulls images, runs `docker compose up -d`, then performs smoke tests. Database migrations are applied automatically on the VMs via cron.

---

## More documentation

- Infrastructure details: `readme-infra.md`
- Deployment, verification, backup/restore: `readme-deploy.md`
