from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.interview import router as interview_router
from utils.logging_config import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Interview Agent API",
    description="Backend for the AI Interview Agent",
    version="1.0.0"
)

# Configure CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(interview_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Interview Agent API is running"}

@app.get("/")
async def root():
    return {
        "message": "AI Interview Agent API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )