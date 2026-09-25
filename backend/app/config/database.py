import os
import ssl
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from app.config.settings import settings

# Ensure upload and storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def normalize_database_url(url: str):
    """
    Normalizes PostgreSQL/NeonDB connection strings to work seamlessly with SQLAlchemy asyncpg.
    """
    if not url:
        return "sqlite+aiosqlite:///./transformiq.db", {}

    if url.startswith("sqlite"):
        return url, {"check_same_thread": False}

    # If it's a postgresql URL
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        # Convert schema to postgresql+asyncpg
        url = re.sub(r"^postgres(ql)?://", "postgresql+asyncpg://", url)

    # Parse and clean query parameters for asyncpg
    parsed = urlparse(url)
    connect_args = {}

    if "asyncpg" in parsed.scheme:
        query_params = parse_qs(parsed.query)
        # Remove unsupported query parameters for asyncpg
        has_ssl = False
        if "sslmode" in query_params or "ssl" in query_params or "neon.tech" in (parsed.hostname or ""):
            has_ssl = True
            query_params.pop("sslmode", None)
            query_params.pop("channel_binding", None)
            query_params.pop("ssl", None)

        # Reconstruct URL without unsupported asyncpg query params
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        url = urlunparse(new_parsed)

        if has_ssl:
            connect_args["ssl"] = "require"

        # NeonDB serverless pooler recommended setting
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_cache_size"] = 0

    return url, connect_args

db_url, db_connect_args = normalize_database_url(settings.DATABASE_URL)

engine_kwargs = {
    "echo": False,
    "connect_args": db_connect_args,
}

if "postgresql" in db_url or "neon.tech" in db_url:
    # Use NullPool for Neon serverless pooler endpoints
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
