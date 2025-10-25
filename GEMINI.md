# Project Overview

Snippetly is a full-stack platform for creating and sharing code fragments.

**Architecture:**

*   **Backend:** A Python API built with FastAPI, using PostgreSQL, Redis, and MongoDB for data storage.
*   **Frontend:** A React application built with Vite and TypeScript.
*   **Containerization:** The entire application is containerized using Docker and managed with `docker-compose`.

**Key Technologies:**

*   **Backend:** FastAPI, SQLAlchemy, Alembic, Beanie, Redis, Pytest, Ruff, Pyright.
*   **Frontend:** React, Vite, TypeScript, SASS, ESLint, Prettier, React Query.
*   **DevOps:** Docker, Docker Compose, GitHub Actions.

# Building and Running

**Prerequisites:**

*   Docker and Docker Compose
*   Node.js and npm (for frontend development)
*   Python and uv (for backend development)

**Running with Docker (Recommended):**

1.  **Copy Environment Variables:**
    ```bash
    cp backend/.env.sample backend/.env
    cp frontend/.env.sample frontend/.env
    ```
2.  **Start the Application:**
    *   For production-like environment:
        ```bash
        docker compose up --build
        ```
    *   For development (with hot-reloading for the backend):
        ```bash
        make up-dev
        ```

**Local Development:**

*   **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
*   **Backend:**
    ```bash
    cd backend
    uv sync
    # Run the development server (refer to FastAPI documentation)
    ```

**Makefile Commands:**

The `Makefile` provides several useful commands for managing the Docker environment:

*   `make up`: Start core services (db, redis).
*   `make up-dev`: Start the full development stack.
*   `make down`: Stop the services.
*   `make logs`: View logs from all services.
*   `make psql`: Access the PostgreSQL database.
*   `make mongo`: Access the MongoDB shell.

# Development Conventions

**Backend:**

*   **Linting:** `ruff` is used for linting. To run the linter:
    ```bash
    cd backend
    uv run ruff check .
    ```
*   **Type Checking:** `pyright` is used for static type checking.
*   **Database Migrations:** `alembic` is used for managing database schema changes.

**Frontend:**

*   **Linting:** `eslint` is used for linting. To run the linter:
    ```bash
    cd frontend
    npm run lint
    ```
*   **Formatting:** `prettier` is used for code formatting. To format the code:
    ```bash
    cd frontend
    npm run format
    ```

**CI/CD:**

The project uses GitHub Actions for CI/CD. The workflow in `.github/workflows/ci.yml` automatically runs linters and builds Docker images on push and pull request events.
