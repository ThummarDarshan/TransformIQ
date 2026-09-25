import os
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.exceptions import HTTPException as StarletteHTTPException
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
    exports,
    tickets,
    provenance,
    uncertainties
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Enforces HTTP security headers to protect against XSS, clickjacking, MIME-sniffing, and MITM.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if settings.ENABLE_SECURITY_HEADERS:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"
            
            # Sensitive API paths shouldn't be cached in shared caches
            if request.url.path.startswith("/api/"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            
            # Strict Transport Security in production / HTTPS
            if settings.STRICT_TRANSPORT_SECURITY and (request.url.scheme == "https" or not settings.DEBUG):
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

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
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# 1. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. CORS configuration with explicit trusted origins
allowed_origins_list = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
if settings.FRONTEND_URL and settings.FRONTEND_URL.strip() not in allowed_origins_list:
    allowed_origins_list.append(settings.FRONTEND_URL.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# 3. Safe Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "message": exc.detail if isinstance(exc.detail, str) else "Request failed"
        },
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "detail": "Input validation error. Please check your submitted fields.",
            "message": "Input validation error. Please check your submitted fields.",
            "errors": [{"field": " -> ".join(str(l) for l in err.get("loc", [])), "message": err.get("msg")} for err in exc.errors()]
        }
    )

@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.error(f"[SECURITY_INCIDENT][ID:{error_id}] Unhandled error at {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "A secure server error occurred. Please contact administrator with your correlation ID.",
            "error_id": error_id
        }
    )

# 4. Include API v1 Routers
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
app.include_router(tickets.router, prefix=settings.API_V1_STR)
app.include_router(provenance.router, prefix=settings.API_V1_STR)
app.include_router(uncertainties.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "product": "TransformIQ — Business Transformation AI",
        "tagline": "From Business Chaos to Implementation-Ready Solutions.",
        "status": "HEALTHY",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in Production",
        "hackathon": "Chaos2Commit 2026"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "transformiq-backend"}
