# Snippetly-API

Snippetly - platform for creating and sharing code fragments


---

## Getting Started

---

### 1. Environment variables

Before running the project, copy the sample environment file:

From the root of the project

On Windows PowerShell use:

```bash
copy backend\config_envs\.env.sample backend\.env
copy frontend\.env.sample frontend\.env
```

On (Linux/macOS):

```bash
cp backend/config_envs/.env.sample backend/.env
cp frontend/.env.sampple frontend/.env
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
* **MongoDB**

---

### 3. Open API documentation

After the backend is running, the interactive API docs are available at:

[http://localhost:8000/docs](http://localhost:8000/docs)

---

### 4. Run tests

Before running the tests, make sure that you have the environment variables set.

On Windows PowerShell use:

```bash
copy backend\config_envs\.env.test.sample backend\.env.test
```

On (Linux/macOS):

```bash
cp backend/config_envs/.env.test.sample backend/.env.test
```

To run the tests:

```bash
make up-test
```

This will run the docker-compose.test.yml file with correct environment file.
