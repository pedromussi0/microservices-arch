from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.routes import v1_router
from app.core.config import settings
from app.core.logger import logger, setup_logging

setup_logging()
# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="E-commerce API with FastAPI",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "192.168.0.141"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API routers
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting application {settings.APP_NAME}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
