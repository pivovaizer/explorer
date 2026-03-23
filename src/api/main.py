from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.blocks import router as blocks_router
from src.api.routers.addresses import router as addresses_router
from src.api.config import settings
from src.api.logger_config import setup_logger


logger = setup_logger(__name__)

app = FastAPI(title="Chia Explorer API", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


app.include_router(blocks_router)
app.include_router(addresses_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.app_env}

