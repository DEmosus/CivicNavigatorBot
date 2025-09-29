from fastapi import APIRouter

from . import auth, chat, incidents, kb, staff

# collect all routers into one
api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(incidents.router)
api_router.include_router(kb.router)
api_router.include_router(staff.router)
