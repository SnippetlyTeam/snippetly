# 🏗️ Snippetly Architecture Documentation

Complete system architecture overview for the Snippetly DevOps project.

---

## 📋 Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Infrastructure Layer](#infrastructure-layer)
3. [Application Layer](#application-layer)
4. [Data Layer](#data-layer)
5. [Deployment Pipeline](#deployment-pipeline)
6. [Security Architecture](#security-architecture)
7. [Monitoring & Observability](#monitoring--observability)
8. [Network Architecture](#network-architecture)

---

## 🌐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS (443)
                         │
         ┌───────────────▼───────────────┐
         │   Azure NSG Firewall          │
         │  - Port 22 (SSH - restricted) │
         │  - Port 80 (HTTP)             │
         │  - Port 443 (HTTPS)           │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   Azure VM (Standard_B2ms)    │
         │   - 2 vCPU, 8GB RAM           │
         │   - Ubuntu 22.04 LTS          │
         │   - Docker + Docker Compose   │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   Docker Network              │
         │   (snippetly-net)             │
         └───────────────┬───────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼────┐        ┌──────▼──────┐      ┌─────▼─────┐
│ nginx  │        │  Frontend   │      │  Backend  │
│ proxy  │───────▶│   (React)   │─────▶│ (FastAPI) │
│ HTTPS  │        │   + Nginx   │      │           │
└────────┘        └─────────────┘      └─────┬─────┘
                                              │
                  ┌───────────────────────────┼───────────────┐
                  │                           │               │
            ┌─────▼─────┐            ┌────────▼────┐   ┌──────▼──────┐
            │ PostgreSQL│            │   Redis     │   │   MongoDB   │
            │    DB     │            │   Cache     │   │  Snippets   │
            └───────────┘            └─────────────┘   └─────────────┘
```

---

## ☁️ Infrastructure Layer

### Azure Resources (Terraform-managed)

```
Azure Subscription
│
├── Resource Group: rg-snippetly
│   │
│   ├── Virtual Network: snippetly-vnet (10.0.0.0/16)
│   │   └── Subnet: snippetly-subnet (10.0.1.0/24)
│   │
│   ├── Network Security Group: snippetly-nsg
│   │   ├── SSH: Port 22 (restricted to allowed_ssh_cidrs)
│   │   ├── HTTP: Port 80 (open)
│   │   └── HTTPS: Port 443 (open)
│   │
│   ├── VM: snippetly-dev-vm (172.201.5.167)
│   │   ├── OS: Ubuntu 22.04 LTS
│   │   ├── Size: Standard_B2ms
│   │   └── Init: cloud-init.sh
│   │
│   ├── VM: snippetly-prod-vm (172.201.26.148)
│   │   ├── OS: Ubuntu 22.04 LTS
│   │   ├── Size: Standard_B2ms
│   │   └── Init: cloud-init.sh
│   │
│   ├── Storage Account: snippetlystor
│   │   ├── Container: media-dev
│   │   ├── Container: media (prod)
│   │   ├── Container: backups-dev
│   │   └── Container: backups (prod)
│   │
│   └── Container Registry: snippetlyacr
│       ├── Repository: snippetly-backend
│       └── Repository: snippetly-frontend
│
└── Resource Group: snippetly-tfstate-rg
    └── Storage Account: snippetlytfstate
        └── Container: tfstate
            └── Blob: snippetly.tfstate
```

---

## 🎯 Application Layer

### Container Architecture (Production)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker Host (VM)                              │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │               Docker Network: snippetly-net                     │ │
│  │                                                                  │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │ │
│  │  │ nginx-proxy  │    │  certbot     │    │   frontend      │  │ │
│  │  │ (HTTPS)      │    │ (Let's       │    │   (React +      │  │ │
│  │  │ Port: 80,443 │    │  Encrypt)    │    │    Nginx)       │  │ │
│  │  │ Limits:      │    │              │    │   Limits:       │  │ │
│  │  │  256M RAM    │    │              │    │    256M RAM     │  │ │
│  │  └──────┬───────┘    └──────────────┘    └────────┬────────┘  │ │
│  │         │                                           │           │ │
│  │         └───────────────────┬───────────────────────┘           │ │
│  │                             │                                   │ │
│  │                   ┌─────────▼──────────┐                        │ │
│  │                   │     backend        │                        │ │
│  │                   │    (FastAPI)       │                        │ │
│  │                   │    Port: 8000      │                        │ │
│  │                   │    Limits:         │                        │ │
│  │                   │     1GB RAM        │                        │ │
│  │                   │     1.0 CPU        │                        │ │
│  │                   └─────────┬──────────┘                        │ │
│  │                             │                                   │ │
│  │         ┌───────────────────┼───────────────────┐               │ │
│  │         │                   │                   │               │ │
│  │    ┌────▼─────┐      ┌──────▼──────┐    ┌──────▼──────┐        │ │
│  │    │celery-   │      │celery-beat  │    │   migrate   │        │ │
│  │    │worker    │      │(scheduler)  │    │  (one-shot) │        │ │
│  │    │Limits:   │      │Limits:      │    │             │        │ │
│  │    │ 768M RAM │      │ 512M RAM    │    │             │        │ │
│  │    └────┬─────┘      └──────┬──────┘    └─────────────┘        │ │
│  │         │                   │                                   │ │
│  │         └───────────────────┼───────────────────┐               │ │
│  │                             │                   │               │ │
│  │                   ┌─────────▼──────┐     ┌──────▼─────┐         │ │
│  │                   │   PostgreSQL   │     │   Redis    │         │ │
│  │                   │   (Database)   │     │  (Cache +  │         │ │
│  │                   │   Port: 5432   │     │   Queue)   │         │ │
│  │                   │   Limits:      │     │  Port: 6379│         │ │
│  │                   │    512M RAM    │     │  Limits:   │         │ │
│  │                   └────────────────┘     │   256M RAM │         │ │
│  │                                          └────────────┘         │ │
│  │                   ┌────────────────┐                            │ │
│  │                   │    MongoDB     │                            │ │
│  │                   │  (Snippets DB) │                            │ │
│  │                   │   Port: 27017  │                            │ │
│  │                   │   Limits:      │                            │ │
│  │                   │    512M RAM    │                            │ │
│  │                   └────────────────┘                            │ │
│  │                                                                  │ │
│  │  Monitoring Stack (Optional):                                   │ │
│  │  ┌──────────────┐    ┌──────────────┐                          │ │
│  │  │ Prometheus   │    │   Grafana    │                          │ │
│  │  │ Port: 9090   │    │  Port: 3000  │                          │ │
│  │  │ (localhost)  │    │  (localhost) │                          │ │
│  │  │ Limits:      │    │  Limits:     │                          │ │
│  │  │  512M RAM    │    │   256M RAM   │                          │ │
│  │  └──────────────┘    └──────────────┘                          │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Persistent Volumes:                                                 │
│  /opt/app-data/postgres  ──▶  PostgreSQL data                       │
│  /opt/app-data/redis     ──▶  Redis persistence                     │
│  /opt/app-data/mongo     ──▶  MongoDB data                          │
│  /opt/app-data/certbot   ──▶  Let's Encrypt certificates            │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 💾 Data Layer

### Database Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Data Storage                              │
│                                                               │
│  PostgreSQL (Relational)          MongoDB (Document)          │
│  ┌─────────────────────┐          ┌──────────────────┐       │
│  │ Users               │          │ Code Snippets    │       │
│  │ - id                │          │ - _id            │       │
│  │ - email             │          │ - user_id        │       │
│  │ - password_hash     │          │ - title          │       │
│  │ - created_at        │          │ - code           │       │
│  │                     │          │ - language       │       │
│  │ Auth Tokens         │          │ - tags           │       │
│  │ - token             │          │ - created_at     │       │
│  │ - user_id           │          │ - updated_at     │       │
│  │ - expires_at        │          └──────────────────┘       │
│  │                     │                                      │
│  │ Sessions            │          Redis (Cache)               │
│  │ - session_id        │          ┌──────────────────┐       │
│  │ - user_id           │          │ Session Data     │       │
│  │ - data              │          │ Cache Keys       │       │
│  └─────────────────────┘          │ Celery Queue     │       │
│                                   │ Rate Limiting    │       │
│                                   └──────────────────┘       │
│                                                               │
│  Azure Blob Storage                                          │
│  ┌────────────────────────────────────────────┐              │
│  │ Media Files:  /media-{env}/                │              │
│  │ Backups:      /backups-{env}/              │              │
│  │   - postgres/pg-backup-*.dump              │              │
│  │   - mongo/mongo-backup-*.archive.gz        │              │
│  │   - redis/redis-backup-*.rdb               │              │
│  └────────────────────────────────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

### Backup Strategy

```
Daily Backups (02:00 UTC):
│
├─▶ PostgreSQL Backup (02:00)
│   ├─ pg_dump → /backups/pg-backup-YYYYMMDD-HHMMSS.dump
│   ├─ Verify: pg_restore --list
│   ├─ Size check: must be > 1KB
│   └─ Upload to: Azure Blob Storage /backups-{env}/postgres/
│
├─▶ MongoDB Backup (02:15)
│   ├─ mongodump --archive --gzip → mongo-backup-*.archive.gz
│   ├─ Verify: gzip -t
│   ├─ Size check: must be > 1KB
│   └─ Upload to: Azure Blob Storage /backups-{env}/mongo/
│
└─▶ Redis Backup (02:30)
    ├─ BGSAVE → dump.rdb
    ├─ Verify: RDB magic number "REDIS"
    ├─ Size check: must be > 100 bytes
    └─ Upload to: Azure Blob Storage /backups-{env}/redis/

Retention: 30 days (Azure Blob lifecycle policy)
```

---

## 🚀 Deployment Pipeline

### CI/CD Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      Developer                                  │
│                         │                                       │
│                git push │                                       │
│                         ▼                                       │
│              ┌──────────────────────┐                           │
│              │   GitHub Repository  │                           │
│              └──────────┬───────────┘                           │
│                         │                                       │
│          ┌──────────────┼──────────────┐                        │
│          │              │              │                        │
│   develop branch    main branch    tags v*                     │
│          │              │              │                        │
│          ▼              ▼              ▼                        │
│   ┌─────────────┐ ┌──────────────┐ ┌──────────────┐           │
│   │  CI/CD Dev  │ │  CI/CD Prod  │ │  CI/CD Prod  │           │
│   └─────┬───────┘ └──────┬───────┘ └──────┬───────┘           │
│         │                │                 │                    │
│         ▼                ▼                 ▼                    │
│   ┌─────────────────────────────────────────────┐              │
│   │        GitHub Actions Workflow               │              │
│   │                                              │              │
│   │  1. Backend Tests                            │              │
│   │     ├─ Ruff lint                             │              │
│   │     ├─ Pyright type-check                    │              │
│   │     └─ Pytest (prod only)                    │              │
│   │                                              │              │
│   │  2. Frontend Tests                           │              │
│   │     ├─ npm run build                         │              │
│   │     └─ npm test (Vitest)                     │              │
│   │                                              │              │
│   │  3. Build & Push Images                      │              │
│   │     ├─ docker build backend                  │              │
│   │     ├─ docker build frontend                 │              │
│   │     └─ docker push to ACR                    │              │
│   │                                              │              │
│   │  4. Deploy to VM                             │              │
│   │     ├─ SSH to VM                             │              │
│   │     ├─ Backup .deploy.env                    │              │
│   │     ├─ Update image tags                     │              │
│   │     ├─ docker compose pull                   │              │
│   │     ├─ docker compose up -d                  │              │
│   │     ├─ Health check                          │              │
│   │     ├─ ✅ Success: remove backup             │              │
│   │     └─ ❌ Failure: rollback                  │              │
│   │                                              │              │
│   └──────────────────┬───────────────────────────┘              │
│                      │                                          │
│                      ▼                                          │
│            ┌──────────────────┐                                 │
│            │   Dev/Prod VM    │                                 │
│            │   Running App    │                                 │
│            └──────────────────┘                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Architecture

### Multi-Layer Security

```
Layer 1: Network Security
│
├─▶ Azure NSG (Network Security Group)
│   ├─ SSH: Port 22 (restricted to allowed_ssh_cidrs)
│   ├─ HTTP: Port 80 (open - redirects to HTTPS)
│   └─ HTTPS: Port 443 (open)
│
Layer 2: VM Security
│
├─▶ fail2ban
│   ├─ SSH brute-force protection
│   ├─ Ban after 3 failed attempts
│   └─ Ban duration: 2 hours
│
├─▶ Firewall (ufw)
│   └─ Configured by cloud-init
│
Layer 3: Application Security
│
├─▶ HTTPS/TLS
│   ├─ Let's Encrypt certificates
│   ├─ TLS 1.2 & 1.3 only
│   ├─ HSTS header
│   └─ Auto-renewal (every 12 hours check)
│
├─▶ Rate Limiting (nginx)
│   ├─ API: 10 req/s per IP
│   ├─ Auth: 5 req/min per IP
│   └─ Password reset: 2 req/hour per IP
│
├─▶ Application Security
│   ├─ JWT authentication
│   ├─ OAuth2 (Google)
│   ├─ Password hashing (bcrypt)
│   └─ CORS configuration
│
Layer 4: Data Security
│
├─▶ Database Access
│   ├─ No external ports exposed
│   ├─ Credentials in .env (not in git)
│   └─ Network isolation (Docker network)
│
└─▶ Secrets Management
    ├─ GitHub Secrets for CI/CD
    ├─ .env files in .gitignore
    └─ Terraform variables (not committed)
```

---

## 📊 Monitoring & Observability

### Metrics Flow

```
┌──────────────────────────────────────────────────────────┐
│                    Application                            │
│                                                           │
│  ┌────────────────┐                                      │
│  │    Backend     │                                      │
│  │   (FastAPI)    │                                      │
│  │                │                                      │
│  │  Middleware:   │                                      │
│  │  ├─ HTTP req   │                                      │
│  │  ├─ Latency    │                                      │
│  │  └─ Errors     │                                      │
│  └────────┬───────┘                                      │
│           │                                               │
│           │ /api/metrics                                  │
│           │ (Prometheus format)                           │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │   Prometheus    │                                     │
│  │   (scrapes      │                                     │
│  │    every 15s)   │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ PromQL queries                                │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │    Grafana      │                                     │
│  │   Dashboards:   │                                     │
│  │  ├─ Overview    │                                     │
│  │  ├─ Requests    │                                     │
│  │  ├─ Latency     │                                     │
│  │  └─ Errors      │                                     │
│  └─────────────────┘                                     │
│           │                                               │
│           │ SSH tunnel                                    │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │   DevOps/Admin  │                                     │
│  │  (localhost:    │                                     │
│  │    3000)        │                                     │
│  └─────────────────┘                                     │
└──────────────────────────────────────────────────────────┘
```

---

## 🌐 Network Architecture

### Production Network Flow

```
Internet
   │
   │ HTTPS (443)
   │
   ▼
┌──────────────────┐
│  snippetly.codes │
│   DNS A Record   │
│  172.201.26.148  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────┐
│   nginx-proxy           │
│   - SSL termination     │
│   - Rate limiting       │
│   - Security headers    │
└────────┬────────────────┘
         │
         ├─▶ /.well-known/acme-challenge/  ──▶  certbot
         │
         ├─▶ /api/*  ──▶  backend:8000
         │                    │
         │                    ├─▶ PostgreSQL:5432
         │                    ├─▶ Redis:6379
         │                    └─▶ MongoDB:27017
         │
         └─▶ /*  ──▶  frontend:80 (React SPA)

Internal Network: snippetly-net (Docker)
- All containers on same network
- Service discovery via container names
- No external ports except nginx-proxy
```

---

## 🔄 Request Flow Example

### User Creates a Snippet

```
1. User (Browser)
   │
   │ POST https://snippetly.codes/api/v1/snippets
   │ Headers: Authorization: Bearer <JWT>
   │ Body: { title, code, language }
   │
   ▼
2. nginx-proxy
   │
   ├─▶ Rate limit check (10 req/s)
   ├─▶ HTTPS termination
   └─▶ Proxy to backend:8000
       │
       ▼
3. FastAPI Backend
   │
   ├─▶ Prometheus middleware (track request)
   ├─▶ JWT authentication
   ├─▶ Validate request body
   │
   ├─▶ Save metadata to PostgreSQL
   │   └─ users, snippets metadata
   │
   ├─▶ Save code to MongoDB
   │   └─ full snippet document
   │
   ├─▶ Cache in Redis
   │   └─ recent snippets list
   │
   └─▶ Return response
       │
       ▼
4. Frontend
   │
   └─▶ Update UI, show new snippet
```

---

## 📚 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Cloud** | Microsoft Azure | Infrastructure hosting |
| **IaC** | Terraform | Infrastructure provisioning |
| **Compute** | Azure VM | Application hosting |
| **Containers** | Docker + Compose | Application runtime |
| **Backend** | FastAPI + Python 3.13 | REST API |
| **Frontend** | React 19 + Vite | SPA |
| **Databases** | PostgreSQL 16 | User data |
| | MongoDB 7 | Code snippets |
| | Redis 7 | Cache + Queue |
| **Queue** | Celery | Background tasks |
| **Web Server** | Nginx | Reverse proxy, SSL |
| **CI/CD** | GitHub Actions | Automation |
| **Monitoring** | Prometheus + Grafana | Metrics & Dashboards |
| **Security** | Let's Encrypt, fail2ban | SSL, SSH protection |
| **Backups** | Azure Blob Storage | Daily backups |

---

## 📈 Scalability Considerations

### Current (Single VM)
- **Capacity**: ~1000 concurrent users
- **Bottleneck**: Single VM resources

### Future Scaling Options

```
Option 1: Vertical Scaling
├─ Upgrade VM size (B4ms → D4s_v3)
├─ Cost: Moderate
└─ Limit: Single VM ceiling

Option 2: Horizontal Scaling
├─ Multiple VMs behind load balancer
├─ Separate DB servers
├─ Redis cluster
└─ Cost: Higher, better reliability

Option 3: Managed Services
├─ Azure App Service (PaaS)
├─ Azure Database for PostgreSQL
├─ Azure Cache for Redis
└─ Cost: Higher, less management
```

---

## 🎓 Design Decisions

### Why Docker Compose (not Kubernetes)?
✅ Simpler for single-VM deployment
✅ Lower resource overhead
✅ Faster iteration
✅ Suitable for pet project scale
❌ Limited horizontal scaling

### Why Nginx proxy (not Traefik)?
✅ Battle-tested, widely known
✅ Better performance
✅ Simpler configuration
❌ Less dynamic service discovery

### Why PostgreSQL + MongoDB (not just one)?
✅ PostgreSQL: Relational user data
✅ MongoDB: Flexible snippet storage
✅ Redis: High-speed caching
✅ Right tool for each job

### Why Azure (not AWS/GCP)?
✅ Good free tier
✅ Simple pricing
✅ Integrated with Azure DevOps
✅ Good for learning

---

**Last Updated**: 2025-12-14
**Maintained By**: Snippetly Team
**Version**: 1.0
