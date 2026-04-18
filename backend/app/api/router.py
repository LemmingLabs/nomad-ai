from fastapi import APIRouter

from app.api.v1.messages import router as messages_router

router = APIRouter()
router.include_router(messages_router)


@router.get("/health")
def health_check():
    return {"status": "Welcome Gay"}
