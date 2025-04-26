"""Main module for initialising and defining the FastAPI application"""

import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import rhythmix_api


API_STR = rhythmix_api.config.SETTINGS.API_STR

APP = fastapi.FastAPI(
    title=rhythmix_api.config.SETTINGS.API_NAME,
    version=rhythmix_api.config.SETTINGS.VERSION,
    openapi_url=f"{API_STR}/openapi.json",
)

# Setting up Routers
API_ROUTER = fastapi.APIRouter()

API_ROUTER.include_router(
    rhythmix_api.v1.routers.model.ROUTER, prefix="/model", tags=["model"]
)

APP.include_router(API_ROUTER, prefix=rhythmix_api.config.SETTINGS.API_STR)

# Setting up CORS
ORIGINS = ["*"]

APP.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# uvicorn main:APP --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        APP,
        host="0.0.0.0",
        port=port,
        log_config=None,  # Disable Uvicorn's default logging to avoid duplication
    )
