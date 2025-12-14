from .favorites import router as favorites_router
from .search import router as search_router
from .snippets import router as snippets_router

snippets_router.include_router(favorites_router)
snippets_router.include_router(search_router)
