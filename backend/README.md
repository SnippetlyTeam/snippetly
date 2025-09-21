# Snippetly-API

---

## **1. Setup virtual environment (Linux/macOS)**

```bash
# Go to the backend directory
cd ~/Projects/works/projects/snippetly\ setup/backend

# Create a virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install uv
uv install --without dev
```

---

## 2. Setup virtual environment (Windows, PowerShell)

```powershell
# Go to the backend directory
cd "C:\path\to\snippetly setup\backend"

# Create a virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install dependencies
pip install uv
uv install --without dev
```

> Make sure you run commands from the **backend directory**, where `main.py` is located inside `src/`.

---

## 3. Run the backend

```bash
# From Linux/macOS
uvicorn src.main:app --port 8000

# From Windows (PowerShell)
uvicorn src.main:app --port 8000
```

* `src.main:app` — tells Uvicorn where the FastAPI app is located.
* `--port 8000` — starts the server on port 8000.

---

## 4. Test the Hello endpoint

Once the server is running, open a browser or Postman and go to:

```
GET http://127.0.0.1:8000/docs/
```

to get OpenAPI