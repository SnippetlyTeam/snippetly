from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routes import v1_router
from src.core.config import get_settings

settings = get_settings()
app = FastAPI(title="Snippetly - API", version="1.0.0", debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api")


@app.get("/hello/")
def hello_world() -> dict:
    return {"msg": "Hello world!"}
