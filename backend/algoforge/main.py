from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from algoforge.config import settings
from algoforge.api.routes import health, data, jobs, strategies, export

app = FastAPI(
    title="AlgoForge API",
    description="AI-Powered Trading Strategy Generator API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
