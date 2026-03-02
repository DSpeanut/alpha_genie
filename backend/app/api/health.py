from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "alpha-genie-api"
    }


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Alpha Genie API",
        "docs": "/docs",
        "health": "/health"
    }
