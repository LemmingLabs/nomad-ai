from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(router)
