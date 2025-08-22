from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.utils.database import connect_db, disconnect_db
from app.routes import meetings, transcription, websocket
from app.config import settings

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    print("🚀 Smart Meeting Assistant API started successfully")
    yield
    # Shutdown
    await disconnect_db()
    print("👋 Smart Meeting Assistant API shutting down")

# Create FastAPI instance
app = FastAPI(
    title="Smart Meeting Assistant API",
    description="AI-Powered Meeting Assistant with real-time transcription and smart features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Smart Meeting Assistant API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smart-meeting-assistant"}

# Include routers
app.include_router(
    meetings.router,
    prefix="/api/v1/meetings",
    tags=["meetings"]
)

app.include_router(
    transcription.router,
    prefix="/api/v1/transcription",
    tags=["transcription"]
)

app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        access_log=True
    )