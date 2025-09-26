# Snippetly-API

---
## Getting Started

---

### 1. Environment variables
Before running the project, copy the sample environment file:

From the root of the project

On Windows PowerShell use: 
```bash
copy backend\.env.sample backend\.env
```

On (Linux/macOS):
```bash
cp backend/.env.sample backend/.env
```
---

### 2. Run with Docker Compose

```bash
docker compose up --build
```

This will start:

* **backend** (FastAPI + Uvicorn)
* **frontend**
* **PostgreSQL** database
* **Redis**

---

### 3. Open API documentation

After the backend is running, the interactive API docs are available at:

 [http://localhost:8000/docs](http://localhost:8000/docs)

---
