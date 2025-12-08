# Snippetly Deployment Guide (Azure)

This guide walks you from zero to a running Snippetly environment on Microsoft Azure using a single Linux VM per environment with Docker Compose. It covers Terraform provisioning, VM setup, application configuration, CI/CD, verification, backups, restore, and troubleshooting.

**Environment Overview:**
- **DEV**: HTTP-only (port 80), accessible via IP address, deploys from `develop` branch
- **PROD**: HTTPS-only (port 443) with Let's Encrypt, accessible via domain (snippetly.codes), deploys from `main` branch

---

## 1. Prerequisites

- Azure subscription with permissions to create Resource Group, VNet/Subnet/NSG, Linux VMs, Storage Account, and Azure Container Registry (ACR).
- Local tools:
  - Terraform >= 1.6
  - Git
  - SSH client (OpenSSH)
  - Optional: Azure CLI (useful to inspect resources, but not required)
  - Optional: Docker (only if you want to build/test locally)
- GitHub repository admin/maintainer permissions to configure Actions secrets.
- SSH public key to access the VMs (`ssh_public_key` variable in Terraform).
- ACR authentication via Service Principal (client ID and password).

---

## 2. Azure preparation (recommended)

- Decide a region (e.g., `westeurope`) and resource group name (e.g., `rg-snippetly`).
- Create an Azure Container Registry (or let Terraform create it) and a Service Principal with push/pull permissions for ACR.
- Choose a globally-unique Storage Account name for Blob Storage (e.g., `snippetlystor12345`).

Optional but recommended CLI prep (if you will run Terraform from an Azure-authenticated shell):

```sh
# 1) Login and select subscription
az login
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"
az account show -o table

# 2) (Optional) Create a Service Principal for ACR push/pull and capture creds
# If ACR is not yet created, you can still create the SP and assign role later.
APP_NAME="snippetly-acr-sp"
SP=$(az ad sp create-for-rbac -n "$APP_NAME" --role AcrPush --scopes \
  "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RG_NAME>/providers/Microsoft.ContainerRegistry/registries/<ACR_NAME>" \
  --sdk-auth)
echo "$SP" | jq .

# Values to save as GitHub Secrets later
# - <ENV>_AZURE_SP_APP_ID    := value of .clientId
# - <ENV>_AZURE_SP_PASSWORD  := value of .clientSecret
# - <ENV>_ACR_LOGIN_SERVER   := <acr_name>.azurecr.io
```

---

## 3. Cloning the Repository

```sh
git clone <your-fork-or-repo-url>
cd snippetly
```

---

## 4. Provision Infrastructure with Terraform

The Terraform code is under `infra/terraform` and defines: Resource Group, VNet, Subnet, NSG (ports 22/80/443 + optional dev ports 8000/5173), two Linux VMs (dev/prod), Storage Account (with media + backups containers), and ACR. It also installs Docker on the VMs via cloud-init and prepares directories for Let's Encrypt certificates.

Create your variables file and apply:

```sh
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your Azure region, ssh key, storage account and ACR names.
 
# Ensure your Azure CLI is logged in to the right subscription (provider auto-detects it):
az account show -o table || az login
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

terraform init
terraform plan
terraform apply
```

### 4.1 Capture useful outputs

```sh
# From infra/terraform directory
DEV_IP=$(terraform output -raw dev_vm_public_ip)
PROD_IP=$(terraform output -raw prod_vm_public_ip)
ACR_LOGIN=$(terraform output -raw acr_login_server)
echo DEV_IP=$DEV_IP PROD_IP=$PROD_IP ACR=$ACR_LOGIN
```

Important variables (see `variables.tf`):
- `location`, `resource_group_name`, `ssh_public_key`, `vm_size`, `admin_username`
- `vnet_cidr`, `subnet_cidr`, `allow_dev_ports`
- `repo_url`, `backend_env_content_dev`, `backend_env_content_prod`
- `storage_account_name`, `media_container_dev`, `media_container_prod`, `backup_container_dev`, `backup_container_prod`
- `acr_name`

Key outputs:
- `dev_vm_public_ip`, `prod_vm_public_ip`
- `storage_account_name`, `media_containers`, `backup_containers`
- `acr_login_server`, `acr_name`, `backend_image_repo`, `frontend_image_repo`

Cloud-init will:
- Install Docker + Compose plugin
- Clone this repo into `/opt/snippetly`
- Create `/opt/snippetly/.deploy.env` for image tags
- Install cron jobs for DB migrations (@reboot + every 10 minutes) and optional nightly backups

---

## 5. Initial VM configuration

SSH to the VM using the public IP from Terraform outputs:

```sh
ssh azureuser@<vm_public_ip>
```

On first boot, cloud-init will have created persistent data directories:
- `/opt/app-data/postgres`, `/opt/app-data/redis`, `/opt/app-data/mongo`
- `/opt/app-data/certbot/conf`, `/opt/app-data/certbot/www` (for Let's Encrypt certificates on prod)

Project layout on the VM:
- `/opt/snippetly` (git clone of this repo)
- `/opt/snippetly/docker-compose.yml` (base compose file)
- `/opt/snippetly/docker-compose.override.yml` (dev environment overlay - exposes ports, adds PGAdmin)
- `/opt/snippetly/docker-compose.prod.yml` (prod environment overlay - adds nginx-proxy + certbot for HTTPS)
- `/opt/snippetly/.deploy.env` will store image tags for deploys

### 5.1 Verify cloud-init completed successfully

```sh
sudo cloud-init status --long
sudo tail -n 200 /var/log/cloud-init-output.log
sudo tail -n 200 /var/log/cloud-init.log
docker --version && docker compose version
```

### 5.2 Cron jobs installed by cloud-init

- Migrations: runs `alembic upgrade head` on @reboot and every 10 minutes.
- Backups (optional): nightly at 02:00 (Postgres) and 02:15 (Mongo), if enabled.

Check:

```sh
crontab -l || true
sudo systemctl status cron --no-pager || sudo systemctl status crond --no-pager || true
```

---

## 6. Preparing backend environment (.env) on the VM

Create the backend `.env`:

```sh
cd /opt/snippetly
cp backend/config_envs/.env.prod.sample backend/.env

# Edit backend/.env and set required values
```

Example `.env` template (do not commit secrets):

```dotenv
# PostgreSQL
POSTGRES_DB=snippetly
POSTGRES_USER=snippetly
POSTGRES_PASSWORD=<secure-password>
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=<secure-password>

# MongoDB
MONGO_DB=snippetly
MONGO_USER=snippetly
MONGO_PASSWORD=<secure-password>
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGO_INITDB_ROOT_USERNAME=snippetly
MONGO_INITDB_ROOT_PASSWORD=<secure-password>
MONGO_INITDB_DATABASE=snippetly

# Security / app
SECRET_KEY_REFRESH=<32+ char random>
SECRET_KEY_ACCESS=<32+ char random>
ENVIRONMENT=production
FRONTEND_URL=http://<vm_public_ip>  # For dev. For prod: https://snippetly.codes

# Email (optional)
EMAIL_APP_PASSWORD=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
FROM_EMAIL=
USE_TLS=true

# OAuth Google (optional)
OAUTH_GOOGLE_CLIENT_SECRET=
OAUTH_GOOGLE_CLIENT_ID=
OAUTH_SSL=false

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account>
# Provide either connection string or account key + optional custom endpoint
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_ACCOUNT_KEY=
AZURE_BLOB_ENDPOINT=
AZURE_MEDIA_CONTAINER=media
AZURE_BACKUP_CONTAINER=backups
```

Notes:
- The frontend container serves static files (HTTP 80) and proxies `/api/` to the backend service on the Docker network.
- SPA uses same-origin `/api/...` calls.

Tips:
- Generate secure secrets quickly:
  ```sh
  python - <<'PY'
  import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(48)))
  PY
  ```
- Get Storage connection string or key using Azure CLI:
  ```sh
  az storage account show-connection-string -g <RG_NAME> -n <STORAGE_ACCOUNT_NAME> -o tsv
  az storage account keys list -g <RG_NAME> -n <STORAGE_ACCOUNT_NAME> -o table
  ```
- Ensure the containers exist (Terraform creates them). To list:
  ```sh
  az storage container list --account-name <STORAGE_ACCOUNT_NAME> --auth-mode login -o table
  ```

### 6.1 Start services the first time

**For DEV environment:**
```sh
cd /opt/snippetly
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
docker compose -f docker-compose.yml -f docker-compose.override.yml ps
```

**For PROD environment (after HTTPS setup - see Section 10.1):**
```sh
cd /opt/snippetly
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

---

## 7. Configuring GitHub Actions Secrets

Create repository secrets for each environment.

Dev (used by `.github/workflows/ci-cd-dev.yml`):
- `DEV_ACR_LOGIN_SERVER` (e.g., `snippetlyacr.azurecr.io`)
- `DEV_AZURE_SP_APP_ID` (Service Principal ID)
- `DEV_AZURE_SP_PASSWORD` (Service Principal password)
- `DEV_SSH_HOST` (VM public IP)
- `DEV_SSH_USER` (e.g., `azureuser`)
- `DEV_SSH_KEY` (private SSH key for the VM)
- `DEV_PUBLIC_URL` (optional; if not set, smoke tests use `http://<DEV_SSH_HOST>`)

Prod (used by `.github/workflows/ci-cd-prod.yml`):
- `PROD_ACR_LOGIN_SERVER`
- `PROD_AZURE_SP_APP_ID`
- `PROD_AZURE_SP_PASSWORD`
- `PROD_SSH_HOST`
- `PROD_SSH_USER`
- `PROD_SSH_KEY`
- `PROD_PUBLIC_URL` (optional; if not set, smoke tests use `http://<PROD_SSH_HOST>`)

What these secrets are for:
- ACR (SP) values are used to log in and push/pull container images.
- SSH values are used by the deploy job to connect to the VM and run `docker compose`.
- PUBLIC_URL, if set, is used by smoke tests; otherwise the pipeline falls back to `http://<SSH_HOST>`.

Step-by-step to collect values:
- ACR login server: from Terraform output `acr_login_server` or Azure Portal → ACR → Login server.
- Create Service Principal (if not yet): see Section 2 commands; ensure it has `AcrPush` on the ACR.
- SSH: use Terraform outputs `dev_vm_public_ip` / `prod_vm_public_ip`, username is `azureuser` by default.
- PUBLIC_URL (optional): if you have a DNS record, set it here for smoke tests.

How to add repository secrets:
- GitHub → your repo → Settings → Secrets and variables → Actions → New repository secret
- Add all `DEV_*` and `PROD_*` listed above.

---

## 8. CI/CD Workflows

**Branching Model:**
- `develop` branch → DEV environment deployment
- `main` branch → PROD environment deployment

**Workflow Details:**

- `.github/workflows/ci-cd-dev.yml`:
  - CI: PRs to `develop` run backend tests (pytest, ruff, pyright) and frontend build
  - CD Dev: push to `develop` branch builds and pushes SHA-tagged images, deploys to dev VM using `docker-compose.yml + docker-compose.override.yml`
  - Concurrency ensures only one dev deployment at a time (in-progress runs canceled)

- `.github/workflows/ci-cd-prod.yml`:
  - CD Prod: push to `main` branch builds and pushes SHA-tagged images (+ latest tag), deploys to prod VM using `docker-compose.yml + docker-compose.prod.yml`
  - Concurrency ensures only one prod deployment at a time (in-progress runs NOT canceled for safety)

- Migrations are handled on the VMs by cron (not in the workflows)

**Image Tagging Strategy:**
- Dev: `<acr_login_server>/snippetly-backend:<commit_sha>`, `<acr_login_server>/snippetly-frontend:<commit_sha>`
- Prod: `<acr_login_server>/snippetly-backend:<commit_sha>` and `latest`, `<acr_login_server>/snippetly-frontend:<commit_sha>` and `latest`

---

## 9. First Deployment – Dev Environment

1) Push code to the `develop` branch (or create a PR and merge to `develop`).
2) Open the GitHub Actions tab → CI/CD Dev workflow → watch the run.
3) Steps performed by the pipeline:
   - Build and push SHA-tagged images to ACR.
   - SSH to the VM, checkout `develop` branch, update `/opt/snippetly/.deploy.env` with image tags.
   - Run `docker compose -f docker-compose.yml -f docker-compose.override.yml pull && up -d` on the VM.

Troubleshooting: SSH into the VM and run:
```sh
docker compose -f docker-compose.yml -f docker-compose.override.yml ps
docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f backend
```

Manual fallback (if pipeline is unavailable):
```sh
ssh azureuser@<DEV_VM_IP>
cd /opt/snippetly
echo "BACKEND_IMAGE=<acr_login_server>/snippetly/backend:<tag>" | sudo tee /opt/snippetly/.deploy.env
echo "FRONTEND_IMAGE=<acr_login_server>/snippetly/frontend:<tag>" | sudo tee -a /opt/snippetly/.deploy.env
docker compose pull
docker compose up -d
```

Smoke tests (manual):
```sh
curl -fsS http://$DEV_IP/api/health && echo OK || echo FAIL
curl -I http://$DEV_IP/ | head -n1
```

---

## 10. Production Deployment

### 10.1 Initial HTTPS Setup (One-Time)

Before the first production deployment, you must obtain Let's Encrypt certificates:

**Prerequisites:**
- DNS A record for `snippetly.codes` and `www.snippetly.codes` must point to the production VM IP (172.201.26.148)
- Production VM is provisioned and accessible via SSH
- Wait 5-10 minutes for DNS propagation after setting up the A record

**Steps:**

1. SSH into the production VM:
```sh
ssh azureuser@<PROD_VM_IP>
cd /opt/snippetly
```

2. Run the HTTPS setup script:
```sh
sudo bash scripts/setup-https-prod.sh your-email@example.com
```

This script will:
- Start the application stack without nginx-proxy
- Temporarily start nginx for ACME HTTP-01 challenge
- Obtain certificates from Let's Encrypt for `snippetly.codes` and `www.snippetly.codes`
- Start the full production stack with HTTPS enabled

3. Verify HTTPS is working:
```sh
curl -I https://snippetly.codes
```

**Certificate Renewal:**
- The `certbot` container automatically checks for renewal twice daily
- Certificates renew automatically 30 days before expiration
- Nginx reloads automatically upon successful renewal

### 10.2 Regular Production Deployments

After initial HTTPS setup, deploy to production by merging to `main`:

```sh
# Merge develop into main (or create PR and merge)
git checkout main
git merge develop
git push origin main
```

The prod workflow (`.github/workflows/ci-cd-prod.yml`) builds and pushes SHA-tagged images to ACR, deploys to the prod VM using `docker-compose.yml + docker-compose.prod.yml`, maintaining HTTPS. If using GitHub Environments, an approval may be required. Migrations are handled by cron on the VM.

---

## 11. Verifying the Deployment

**DEV Environment:**
- Frontend: http://<DEV_VM_IP>
- Backend docs: http://<DEV_VM_IP>/api/docs
- Health: http://<DEV_VM_IP>/api/health
- Direct backend access (if dev ports enabled): http://<DEV_VM_IP>:8000/api/docs

**PROD Environment:**
- Frontend: https://snippetly.codes
- Backend docs: https://snippetly.codes/api/docs
- Health: https://snippetly.codes/api/health
- HTTP redirect test: curl -I http://snippetly.codes (should return 301 to HTTPS)

**Check containers on VM:**

DEV:
```sh
ssh azureuser@<DEV_VM_IP>
cd /opt/snippetly
docker compose -f docker-compose.yml -f docker-compose.override.yml ps
docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f backend
```

PROD:
```sh
ssh azureuser@<PROD_VM_IP>
cd /opt/snippetly
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f nginx-proxy
```

---

## 12. Rollback

- On VM, edit `/opt/snippetly/.deploy.env` to set previous image tags for `BACKEND_IMAGE` and `FRONTEND_IMAGE`, then:

```sh
set -e
docker pull "$BACKEND_IMAGE" || true
docker pull "$FRONTEND_IMAGE" || true
docker compose up -d
```

---

## 13. Manual Backups – How to Run

Two backup helper scripts are provided (run on the VM):

```sh
chmod +x /opt/snippetly/scripts/backup_pg.sh
chmod +x /opt/snippetly/scripts/backup_mongo.sh

# PostgreSQL backup
/opt/snippetly/scripts/backup_pg.sh

# MongoDB backup
/opt/snippetly/scripts/backup_mongo.sh

What the scripts do:
- Exec into the DB containers to run `pg_dump` (Postgres) or `mongodump` (MongoDB).
- Copy the resulting archive to the host and into the backend container.
- Use `backend/ops/upload_to_azure.py` to upload to Azure Blob Storage.

Backups are uploaded to the configured Azure Blob Storage container (set `AZURE_BACKUP_CONTAINER` in backend `.env`, otherwise `AZURE_MEDIA_CONTAINER` is used). Objects are stored under prefixes:
- `backups/postgres/`
- `backups/mongo/`

Cron suggestion on the VM (edit with `crontab -e`):
```
0 2 * * * /bin/bash /opt/snippetly/scripts/backup_pg.sh >> /var/log/snippetly_backups.log 2>&1
15 2 * * * /bin/bash /opt/snippetly/scripts/backup_mongo.sh >> /var/log/snippetly_backups.log 2>&1
```

Validate backups landed in Blob:
```sh
az storage blob list --container-name <AZURE_BACKUP_CONTAINER> \
  --account-name <STORAGE_ACCOUNT_NAME> --auth-mode login -o table
```

---

## 14. Restore – High-level Procedure

- PostgreSQL: download desired `.dump` from Object Storage → copy to `db` container → `pg_restore -U $POSTGRES_USER -d $POSTGRES_DB -c <file.dump>` (stop app or set maintenance mode if needed).
- MongoDB: download `.archive.gz` → copy to `mongodb` container → `mongorestore --gzip --archive=<file> --drop`.

Ensure credentials in `backend/.env` are correct before restore.

Example commands:
```sh
# Postgres
scp <backup.dump> azureuser@<vm_ip>:/tmp/
ssh azureuser@<vm_ip> "docker cp /tmp/backup.dump db:/backup.dump && docker exec -it db \
  bash -lc 'pg_restore -U $POSTGRES_USER -d $POSTGRES_DB -c /backup.dump'"

# Mongo
scp <backup.archive.gz> azureuser@<vm_ip>:/tmp/
ssh azureuser@<vm_ip> "docker cp /tmp/backup.archive.gz mongodb:/backup.archive.gz && docker exec -it mongodb \
  bash -lc 'mongorestore --gzip --archive=/backup.archive.gz --drop'"
```

---

## 15. Working with Celery

Enabled in server compose:
- `celery-worker` runs background tasks.
- `celery-beat` runs periodic schedules.

Inspect and manage:
```sh
docker compose ps
docker compose logs -f celery-worker
docker compose logs -f celery-beat

# Scale workers
docker compose up -d --scale celery-worker=2
```

---

## 16. Troubleshooting

- ACR login fails in CI/CD: verify `*_ACR_LOGIN_SERVER` and Service Principal credentials.
- Migration step fails: check DB connection values in `backend/.env`; verify `db` container is healthy.
- Smoke test fails: check that `DEV_PUBLIC_URL`/`PROD_PUBLIC_URL` (if set) is correct; verify `frontend` and `backend` containers are running and healthy.
- SSH connection from Actions fails: verify `*_SSH_*` secrets and VM network/NSG rules (22 open).
- Inspect services on VM:
  - `docker compose ps`
  - `docker compose logs -f <service>`
  - `systemctl status docker` (Docker service)
 - Check cloud-init logs if VM did not bootstrap:
   - `sudo cloud-init status --long`
   - `sudo tail -n 200 /var/log/cloud-init-output.log`
 - Check network/ports on VM:
   - `ss -lntp | egrep ':22|:80'`
 - Verify NSG has inbound 22 and 80 open to your source as expected.
 - Test ACR pull from VM (auth optional if ACR is private and no admin enabled):
   - `docker login <acr_login_server>` then `docker pull <acr_login_server>/snippetly/backend:<tag>`

---

## 17. Notes & Future Improvements

- ✅ HTTPS implemented via Nginx reverse proxy + Let's Encrypt certbot (Production)
- Export Docker logs to Azure Monitor/Log Analytics
- Consider managed DB services, or separate VMs for DB/Redis/Mongo
- Consider AKS migration if more services or higher scale are needed
- Implement rate limiting and WAF rules in nginx-proxy
- Add monitoring and alerting for certificate expiration (though auto-renewal is configured)

---

## 18. Destroying Infrastructure

To remove all provisioned Azure resources created by Terraform:

```sh
cd infra/terraform
terraform destroy
```

---

## Appendix A. Dev end-to-end quickstart (commands)

```sh
# Local shell
az login && az account set --subscription "<SUBSCRIPTION_ID>"
cd infra/terraform && terraform init && terraform apply -auto-approve

# Copy backend env and edit secrets on the dev VM
ssh azureuser@$(terraform output -raw dev_vm_public_ip)
cd /opt/snippetly && cp backend/config_envs/.env.prod.sample backend/.env && nano backend/.env

# Configure GitHub Secrets (DEV_*) with ACR SP + SSH + optional DEV_PUBLIC_URL

# Trigger deployment to dev by pushing to develop branch
git checkout develop
git commit --allow-empty -m "test deploy"
git push origin develop
```

## Appendix B. Prod release checklist

- All DEV checks passed; backups configured and verified.
- Set PROD_* secrets (ACR SP, SSH, PROD_PUBLIC_URL should be https://snippetly.codes).
- **One-time:** Run HTTPS setup script on prod VM (see Section 10.1).
- DNS A record for snippetly.codes points to prod VM IP.
- Merge develop into main and push:
  ```sh
  git checkout main
  git merge develop
  git push origin main
  ```
- Monitor the prod workflow run; verify HTTPS is working.
- Test: curl -I https://snippetly.codes
- Verify HTTP→HTTPS redirect: curl -I http://snippetly.codes
- Document the deployed commit SHA in release notes.
