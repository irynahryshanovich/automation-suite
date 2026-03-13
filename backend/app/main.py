from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router as api_router
from app.database import init_db
from app.scheduler import init_scheduler, scheduler


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup: initialize database and scheduler
    init_db()
    init_scheduler()
    yield
    # Shutdown: stop the background scheduler gracefully
    scheduler.shutdown()


# Initialize FastAPI app
app = FastAPI(
    title="Automation Suite API",
    description="API for a miniaturized automation suite for managing social media actions",
    version="1.0.0",
    lifespan=lifespan,
)


# Configure CORS to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)