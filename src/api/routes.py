# src/api/routes.py
"""
Route registration for all API endpoints.
"""

from fastapi import APIRouter
from src.api.endpoints import candidates, jobs, screening, auth  # ✅ include auth

# Create main router
api_router = APIRouter(prefix="/api")

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])  # ✅ add this
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(screening.router, prefix="/screening", tags=["Screening"])