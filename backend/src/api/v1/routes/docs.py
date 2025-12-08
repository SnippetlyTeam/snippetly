from typing import Dict, Any

from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from src.core.config import get_settings
from src.core.dependencies.accounts import is_admin

router = APIRouter()

settings = get_settings()


@router.get(
    settings.DOCS_URL,
    include_in_schema=False,
    dependencies=[Depends(is_admin)],
)
def custom_swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json/", title="Docs")


@router.get(
    settings.REDOC_URL,
    include_in_schema=False,
    dependencies=[Depends(is_admin)],
)
def custom_redoc_html() -> HTMLResponse:
    return get_redoc_html(openapi_url="/openapi.json/", title="Redoc")


@router.get(
    settings.OPENAPI_URL,
    include_in_schema=False,
    dependencies=[Depends(is_admin)],
)
def custom_openapi() -> Dict[str, Any]:
    from src.main import app

    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
