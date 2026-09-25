import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import engine, Base, AsyncSessionLocal
from app.api.v1 import (
    auth,
    workspaces,
    projects,
    documents,
    discovery,
    business_analysis,
    gaps,
    recommendations,
    architecture,
    processes,
    database_design,
    apis,
    ux_design,
    planning,
    risks,
    scores,
    simulations,
    blueprints,
    collaboration,
    admin,
    exports
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure table schemas exist without blocking server readiness
    async def init_db():
        try:
            logger.info("Verifying database schema...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            logger.info("TransformIQ Backend Engine ready with clean database.")
        except Exception as e:
            logger.warning(f"Database schema check notice: {e}")

    import asyncio
    asyncio.create_task(init_db())
    logger.info("TransformIQ Backend Engine startup initialized.")
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Business Transformation AI (AI Solution Builder) — Converts enterprise business chaos, prompts, and documents into implementation-ready blueprints.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Include API v1 Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(workspaces.org_router, prefix=settings.API_V1_STR)
app.include_router(workspaces.ws_router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(discovery.router, prefix=settings.API_V1_STR)
app.include_router(business_analysis.router, prefix=settings.API_V1_STR)
app.include_router(gaps.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(architecture.router, prefix=settings.API_V1_STR)
app.include_router(processes.router, prefix=settings.API_V1_STR)
app.include_router(database_design.router, prefix=settings.API_V1_STR)
app.include_router(apis.router, prefix=settings.API_V1_STR)
app.include_router(ux_design.router, prefix=settings.API_V1_STR)
app.include_router(planning.router, prefix=settings.API_V1_STR)
app.include_router(risks.router, prefix=settings.API_V1_STR)
app.include_router(scores.router, prefix=settings.API_V1_STR)
app.include_router(simulations.router, prefix=settings.API_V1_STR)
app.include_router(blueprints.router, prefix=settings.API_V1_STR)
app.include_router(collaboration.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(exports.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "product": "TransformIQ — Business Transformation AI",
        "tagline": "From Business Chaos to Implementation-Ready Solutions.",
        "status": "HEALTHY",
        "version": settings.VERSION,
        "docs": "/docs",
        "hackathon": "Chaos2Commit 2026"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "transformiq-backend"}
