"""
main.py
-------
FastAPI app entrypoint. Run from the backend/ directory:
    uvicorn main:app --reload --port 8000
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.interview import router as interview_router


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Interview Agent API",
    description="Backend for the AI Interview Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Interview Agent API is running"}


@app.get("/")
async def root():
    return {"message": "AI Interview Agent API", "docs": "/docs", "health": "/health"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)