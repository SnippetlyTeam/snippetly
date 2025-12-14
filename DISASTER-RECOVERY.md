# 🚨 Disaster Recovery Runbook

Complete disaster recovery procedures for Snippetly.

**Target RTO (Recovery Time Objective)**: 2 hours
**Target RPO (Recovery Point Objective)**: 24 hours (daily backups)

---

## 📋 Table of Contents

1. [Emergency Contacts](#emergency-contacts)
2. [Disaster Scenarios](#disaster-scenarios)
3. [Pre-Recovery Checklist](#pre-recovery-checklist)
4. [Recovery Procedures](#recovery-procedures)
5. [Post-Recovery Verification](#post-recovery-verification)
6. [Prevention Measures](#prevention-measures)

---

## 📞 Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| Infrastructure Owner | TBD | 24/7 |
| Backup Admin | TBD | 24/7 |
| Database Admin | TBD | Business hours |
| On-call Engineer | TBD | Rotation |

**Escalation Path:**
Engineer → Backup Admin → Infrastructure Owner

---

## 💥 Disaster Scenarios

### Scenario Matrix

| Scenario | Severity | RTO | RPO | Procedure |
|----------|----------|-----|-----|-----------|
| VM failure | 🔴 Critical | 2h | 24h | [#1 Full VM Recovery](#1-full-vm-recovery) |
| Database corruption | 🔴 Critical | 1h | 24h | [#2 Database Recovery](#2-database-recovery) |
| Application crash | 🟡 High | 15m | 0h | [#3 Application Recovery](#3-application-recovery) |
| Accidental data deletion | 🟡 High | 30m | 24h | [#4 Data Restoration](#4-data-restoration) |
| SSL certificate expired | 🟡 High | 30m | 0h | [#5 SSL Recovery](#5-ssl-certificate-recovery) |
| Storage full | 🟠 Medium | 1h | 0h | [#6 Storage Cleanup](#6-storage-full-recovery) |
| DDoS attack | 🟠 Medium | 1h | 0h | [#7 DDoS Mitigation](#7-ddos-mitigation) |
| Terraform state corruption | 🔴 Critical | 4h | N/A | [#8 State Recovery](#8-terraform-state-recovery) |

---

## ✅ Pre-Recovery Checklist

Before starting any recovery:

- [ ] **Assess Impact**: What is broken? What is still working?
- [ ] **Document Current State**: Screenshots, logs, error messages
- [ ] **Notify Stakeholders**: Inform users about downtime
- [ ] **Verify Backups**: Check latest backup date/time
- [ ] **Prepare Rollback**: Plan B if recovery fails
- [ ] **Get Required Access**: SSH keys, Azure portal, GitHub

---

## 🔧 Recovery Procedures

### #1 Full VM Recovery

**Scenario**: VM destroyed, corrupted, or unresponsive

**Prerequisites:**
- Terraform code available
- Azure access configured
- Backups in Azure Blob Storage

**Steps:**

#### 1.1 Provision New VM

```bash
# Navigate to Terraform directory
cd infra/terraform

# Verify credentials
az account show

# Initialize Terraform (pulls remote state)
terraform init

# Plan recovery (check what will be created)
terraform plan -out=recovery.tfplan

# Apply (create new VM)
terraform apply recovery.tfplan
```

**Expected time**: 10-15 minutes

#### 1.2 Wait for Cloud-Init

```bash
# SSH to new VM
ssh azureuser@<NEW_VM_IP>

# Check cloud-init status
sudo cloud-init status --wait

# Verify services are running
docker ps

# Expected: db, redis, mongodb, backend, celery containers
```

**Expected time**: 5-10 minutes

#### 1.3 Restore Backups

```bash
# On the new VM
cd /opt/snippetly

# Download latest backups from Azure Blob
./scripts/restore_all.sh
```

**Create restore script** (`scripts/restore_all.sh`):

```bash
#!/bin/bash
set -euo pipefail

echo "🔄 Starting full disaster recovery..."

# Source backend environment
cd /opt/snippetly
source backend/.env

BACKUP_DATE="${1:-latest}"

# Download latest backups
echo "📥 Downloading backups from Azure..."
az storage blob download \
  --container-name backups \
  --name "postgres/pg-backup-$BACKUP_DATE.dump" \
  --file /tmp/pg-restore.dump \
  --account-name $AZURE_STORAGE_ACCOUNT_NAME

az storage blob download \
  --container-name backups \
  --name "mongo/mongo-backup-$BACKUP_DATE.archive.gz" \
  --file /tmp/mongo-restore.archive.gz \
  --account-name $AZURE_STORAGE_ACCOUNT_NAME

az storage blob download \
  --container-name backups \
  --name "redis/redis-backup-$BACKUP_DATE.rdb" \
  --file /tmp/redis-restore.rdb \
  --account-name $AZURE_STORAGE_ACCOUNT_NAME

# Restore PostgreSQL
echo "📦 Restoring PostgreSQL..."
docker compose exec -T db pg_restore -U $POSTGRES_USER -d $POSTGRES_DB \
  --clean --if-exists < /tmp/pg-restore.dump

# Restore MongoDB
echo "📦 Restoring MongoDB..."
docker compose exec -T mongodb mongorestore \
  --archive=/tmp/mongo-restore.archive.gz \
  --gzip \
  --username $MONGO_INITDB_ROOT_USERNAME \
  --password $MONGO_INITDB_ROOT_PASSWORD \
  --authenticationDatabase admin \
  --drop

# Restore Redis
echo "📦 Restoring Redis..."
docker compose stop redis
cp /tmp/redis-restore.rdb /opt/app-data/redis/dump.rdb
docker compose start redis

echo "✅ Recovery complete!"
```

**Expected time**: 10-15 minutes

#### 1.4 Verify Application

```bash
# Check all containers are healthy
docker compose ps

# Test health endpoint
curl http://localhost/api/health

# Check logs
docker compose logs backend | tail -50
```

**Expected time**: 5 minutes

**Total RTO: ~45-60 minutes**

---

### #2 Database Recovery

**Scenario**: PostgreSQL or MongoDB data corruption

#### 2.1 PostgreSQL Recovery

```bash
# Stop backend to prevent writes
docker compose stop backend celery-worker celery-beat

# List available backups
az storage blob list \
  --container-name backups \
  --prefix "postgres/" \
  --account-name snippetlystor

# Download specific backup
BACKUP_DATE="20250101-020000"
az storage blob download \
  --container-name backups \
  --name "postgres/pg-backup-$BACKUP_DATE.dump" \
  --file /tmp/pg-restore.dump

# Restore database
docker compose exec -T db psql -U snippetly -c "DROP DATABASE IF EXISTS snippetly;"
docker compose exec -T db psql -U snippetly -c "CREATE DATABASE snippetly;"
docker compose exec -T db pg_restore \
  -U snippetly -d snippetly \
  --clean --if-exists < /tmp/pg-restore.dump

# Restart application
docker compose start backend celery-worker celery-beat

# Verify
docker compose logs backend | grep "Started"
```

**RTO: ~20 minutes**

#### 2.2 MongoDB Recovery

```bash
# Stop services
docker compose stop backend celery-worker celery-beat

# Download backup
BACKUP_DATE="20250101-021500"
az storage blob download \
  --container-name backups \
  --name "mongo/mongo-backup-$BACKUP_DATE.archive.gz" \
  --file /tmp/mongo-restore.archive.gz

# Restore
docker compose exec -T mongodb mongorestore \
  --archive=/tmp/mongo-restore.archive.gz \
  --gzip \
  --username snippetly \
  --password mongodb \
  --authenticationDatabase admin \
  --db snippetly \
  --drop

# Restart
docker compose start backend celery-worker celery-beat
```

**RTO: ~15 minutes**

---

### #3 Application Recovery

**Scenario**: Backend crashed, container not responding

#### 3.1 Quick Restart

```bash
# Check container status
docker compose ps

# View logs
docker compose logs backend --tail=100

# Restart specific service
docker compose restart backend

# Or restart all
docker compose restart
```

**RTO: 2-5 minutes**

#### 3.2 Rollback Deployment

```bash
# If recent deployment caused issue
cd /opt/snippetly

# Restore previous version
if [ -f .deploy.env.bak ]; then
  mv .deploy.env.bak .deploy.env
  docker compose pull
  docker compose up -d
fi
```

**RTO: 5-10 minutes**

---

### #4 Data Restoration

**Scenario**: User accidentally deleted important data

#### 4.1 Point-in-Time Recovery

```bash
# List available backups
az storage blob list \
  --container-name backups \
  --prefix "postgres/" \
  | grep "20250114"  # Date before deletion

# Download backup before deletion
az storage blob download \
  --container-name backups \
  --name "postgres/pg-backup-20250114-020000.dump" \
  --file /tmp/recovery.dump

# Extract specific table/data
docker compose exec -T db pg_restore \
  -U snippetly -d snippetly \
  --table=users \
  --data-only \
  --if-exists < /tmp/recovery.dump

# Or restore to temp database for data extraction
docker compose exec -T db psql -U snippetly -c "CREATE DATABASE recovery_temp;"
docker compose exec -T db pg_restore \
  -U snippetly -d recovery_temp < /tmp/recovery.dump

# Extract needed data
docker compose exec -T db psql -U snippetly -d recovery_temp \
  -c "SELECT * FROM users WHERE id = 123;"
```

**RTO: 15-30 minutes**

---

### #5 SSL Certificate Recovery

**Scenario**: Let's Encrypt certificate expired or corrupted

#### 5.1 Force Certificate Renewal

```bash
# Stop nginx-proxy to free port 80
docker compose stop nginx-proxy

# Run certbot manually
docker compose run --rm certbot certonly \
  --standalone \
  --email admin@snippetly.codes \
  --agree-tos \
  --force-renewal \
  -d snippetly.codes \
  -d www.snippetly.codes

# Restart nginx
docker compose start nginx-proxy

# Verify
curl -I https://snippetly.codes
```

**RTO: 10 minutes**

#### 5.2 Use Staging Certificate (Emergency)

```bash
# If production rate-limited, use staging
docker compose run --rm certbot certonly \
  --standalone \
  --server https://acme-staging-v02.api.letsencrypt.org/directory \
  --email admin@snippetly.codes \
  --agree-tos \
  -d snippetly.codes
```

---

### #6 Storage Full Recovery

**Scenario**: Disk space at 100%

#### 6.1 Emergency Cleanup

```bash
# Check disk usage
df -h
du -sh /opt/app-data/*
du -sh /var/lib/docker/*

# Clean Docker
docker system prune -af --volumes
# WARNING: This removes unused volumes!

# Clean old logs
sudo journalctl --vacuum-time=7d
sudo rm -f /var/log/*.gz

# Clean old backups (keep last 7 days)
find /opt/snippetly/backups -mtime +7 -delete

# Clean Docker build cache
docker builder prune -af
```

**RTO: 15 minutes**

---

### #7 DDoS Mitigation

**Scenario**: Application under attack

#### 7.1 Immediate Response

```bash
# Check current traffic
docker compose logs nginx-proxy | grep "429 Too Many Requests"

# Tighten rate limits (infra/nginx/prod-nginx.conf)
# Change: rate=10r/s → rate=5r/s
# Change: rate=5r/m → rate=3r/m

# Reload nginx
docker compose exec nginx-proxy nginx -s reload

# Block specific IP
docker compose exec nginx-proxy sh -c \
  'echo "deny 192.0.2.1;" >> /etc/nginx/conf.d/blocklist.conf'
docker compose exec nginx-proxy nginx -s reload
```

#### 7.2 Enable Azure DDoS Protection

```bash
# Via Terraform
cd infra/terraform

# Add to network.tf
resource "azurerm_network_ddos_protection_plan" "ddos" {
  name                = "snippetly-ddos"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

terraform apply
```

**RTO: 30 minutes**

---

### #8 Terraform State Recovery

**Scenario**: Terraform state corrupted or lost

#### 8.1 State Recovery from Azure

```bash
cd infra/terraform

# Download state from Azure Storage
az storage blob download \
  --account-name snippetlytfstate \
  --container-name tfstate \
  --name snippetly.tfstate \
  --file terraform.tfstate

# Or pull from backend
terraform init
terraform state pull > terraform.tfstate.backup

# Verify
terraform plan
```

#### 8.2 State Import (If Lost)

```bash
# Import existing resources
terraform import azurerm_resource_group.rg /subscriptions/.../resourceGroups/rg-snippetly
terraform import azurerm_virtual_network.vnet /subscriptions/.../virtualNetworks/snippetly-vnet
# ... repeat for all resources

# Verify
terraform plan
# Should show: No changes. Infrastructure is up-to-date.
```

**RTO: 2-4 hours**

---

## ✅ Post-Recovery Verification

After any recovery, verify:

### Application Checks

```bash
# 1. Health endpoint
curl http://localhost/api/health
# Expected: {"status": "ok"}

# 2. Database connectivity
docker compose exec backend python -c "from src.db import engine; print(engine.connect())"

# 3. All containers running
docker compose ps
# Expected: All containers Up (healthy)

# 4. Disk space
df -h /
# Expected: < 80% used

# 5. Logs clean
docker compose logs --tail=50
# Expected: No errors
```

### User-Facing Checks

```bash
# 1. Homepage loads
curl -I https://snippetly.codes
# Expected: 200 OK

# 2. Login works
curl -X POST https://snippetly.codes/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# 3. Create snippet
curl -X POST https://snippetly.codes/api/v1/snippets \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"Test","code":"print(1)"}'
```

### Monitoring Checks

```bash
# 1. Prometheus targets
curl http://localhost:9090/api/v1/targets
# Expected: All targets UP

# 2. Grafana accessible
curl http://localhost:3000/api/health
# Expected: {"commit":"...","database":"ok"}
```

---

## 🛡️ Prevention Measures

### Daily

- ✅ Automated backups (02:00 UTC)
- ✅ Backup verification
- ✅ Health checks

### Weekly

- [ ] Review logs for errors
- [ ] Check disk usage
- [ ] Verify SSL certificate validity

### Monthly

- [ ] Test backup restoration (dry run)
- [ ] Review and update this runbook
- [ ] Update dependencies
- [ ] Rotate secrets

### Quarterly

- [ ] Full DR drill
- [ ] Review RTO/RPO targets
- [ ] Update emergency contacts

---

## 📚 Reference Materials

### Important Locations

| Item | Location |
|------|----------|
| Backups | Azure Blob: `/backups-{env}/` |
| Terraform State | Azure Blob: `snippetlytfstate/tfstate/` |
| SSL Certificates | VM: `/opt/app-data/certbot/conf/` |
| Application Data | VM: `/opt/app-data/{postgres,mongo,redis}/` |
| Logs | Docker: `docker compose logs` |

### Quick Commands

```bash
# Show all backups
az storage blob list --container-name backups --account-name snippetlystor

# Download latest backup
az storage blob download \
  --container-name backups \
  --name "postgres/pg-backup-latest.dump" \
  --file /tmp/restore.dump

# Check service health
docker compose ps
docker compose logs backend --tail=50

# Restart everything
docker compose restart

# Emergency stop
docker compose down
```

---

## 🚨 Escalation Triggers

**Immediate escalation if:**

- ❌ RTO exceeded by >50%
- ❌ Data loss detected (beyond RPO)
- ❌ Security breach suspected
- ❌ Multiple recovery attempts failed
- ❌ Unknown disaster scenario

**Escalation Process:**

1. Document incident details
2. Contact Infrastructure Owner
3. Engage Azure Support (if needed)
4. Schedule post-incident review

---

## 📝 Incident Report Template

After recovery, document:

```markdown
## Incident Report

**Date**: YYYY-MM-DD
**Duration**: HH:MM
**Severity**: Critical/High/Medium/Low

### Summary
What happened?

### Impact
- Users affected: X
- Services down: Y
- Data lost: Z

### Root Cause
Why did it happen?

### Resolution
How was it fixed?

### Prevention
How to prevent recurrence?

### Action Items
- [ ] Update monitoring
- [ ] Update runbook
- [ ] Schedule follow-up
```

---

## 🎓 Training

**New team members should:**

1. Read this runbook thoroughly
2. Practice backup restoration (dev environment)
3. Simulate VM recovery (test VM)
4. Review with senior engineer

**Recommended practice frequency:**
- Individual: Monthly
- Team drill: Quarterly

---

**Last Updated**: 2025-12-14
**Next Review**: 2025-03-14
**Owner**: DevOps Team
**Version**: 1.0

---

## Emergency Hotline

**Critical Issues**: Call Infrastructure Owner immediately
**Non-critical**: Create GitHub issue, tag @devops

**Remember**: Stay calm, follow the runbook, document everything.
