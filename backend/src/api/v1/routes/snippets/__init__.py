from .favorites import router as favorites_router
from .snippets import router as snippets_router

snippets_router.include_router(favorites_router)
