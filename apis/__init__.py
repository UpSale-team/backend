from fastapi import APIRouter
#import routes from src folder
from .v1.routes.auth import router as auth_router
from .v1.routes.knowledge import router as knowledge_router
from .v1.routes.user import router as user_router
from .v1.routes.project import router as project_router
from .v1.routes.rag import router as rag_router

#Register routes for the src API
api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(project_router)
