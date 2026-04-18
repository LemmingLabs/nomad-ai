from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

router = APIRouter()
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
router.include_router(api_v1_router)


@router.get("/health")
def health_check():
    return {"status": "OK"}
