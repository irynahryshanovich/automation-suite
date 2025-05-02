from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router as api_router
from app.database import init_db
from app.scheduler import init_scheduler

# Initialize FastAPI app
app = FastAPI(
    title="Automation Suite API",
    description="API for a miniaturized automation suite for managing social media actions",
    version="1.0.0",
)

# Configure CORS to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database and scheduler on startup"""
    init_db()
    init_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)