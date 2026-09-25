import pytest
import pytest_asyncio
import uuid
import time
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from app.main import app
from app.config.database import AsyncSessionLocal
from app.config.settings import settings
from app.models.user import User, UserRole, Organization, Workspace, ProjectMember
from app.models.project import Project, Document
from app.auth.security import (
    get_password_hash,
    create_access_token,
    revoke_token,
    validate_password_strength
)
from app.auth.rate_limiter import limiter
from seed_rbac_demo import seed_rbac

@pytest_asyncio.fixture(autouse=True, scope="module")
async def setup_security_test_environment():
    await seed_rbac()
    limiter.reset()

# =========================================================================
# 1. AUTHENTICATION & PASSWORD SECURITY TESTS
# =========================================================================

@pytest.mark.asyncio
async def test_auth_wrong_password_uniform_error():
    """Verify login failure returns generic message and prevents user enumeration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Non-existent user
        resp1 = await ac.post("/api/v1/auth/login", json={
            "email": "nonexistent_user_99@transformiq.local",
            "password": "WrongPassword@2026"
        })
        assert resp1.status_code == 401
        assert "Invalid email or password" in resp1.json()["detail"]

        # Existing user, wrong password
        resp2 = await ac.post("/api/v1/auth/login", json={
            "email": "admin@transformiq.local",
            "password": "WrongPassword@2026"
        })
        assert resp2.status_code == 401
        assert "Invalid email or password" in resp2.json()["detail"]

@pytest.mark.asyncio
async def test_auth_weak_password_rejected():
    """Verify weak passwords fail validation during registration."""
    weak_passwords = ["12345", "password", "short1", "ALLUPPERCASE1", "alllowercase1"]
    for pwd in weak_passwords:
        is_strong, msg = validate_password_strength(pwd)
        assert is_strong is False

@pytest.mark.asyncio
async def test_auth_strong_password_accepted():
    """Verify strong passwords meet OWASP ASVS complexity requirements."""
    is_strong, _ = validate_password_strength("SecureTransformation@2026")
    assert is_strong is True

@pytest.mark.asyncio
async def test_auth_logout_revokes_token():
    """Verify logging out revokes the token and prevents further access."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()

    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Access protected endpoint -> 200
        resp1 = await ac.get("/api/v1/auth/me", headers=headers)
        assert resp1.status_code == 200
        
        # 2. Call logout
        resp_logout = await ac.post("/api/v1/auth/logout", headers=headers)
        assert resp_logout.status_code == 200
        assert resp_logout.json()["success"] is True

        # 3. Access protected endpoint with revoked token -> 401
        resp2 = await ac.get("/api/v1/auth/me", headers=headers)
        assert resp2.status_code == 401
        assert "revoked" in resp2.json()["detail"].lower()

@pytest.mark.asyncio
async def test_auth_change_password_requires_correct_current():
    """Verify changing password validates current password and requires complexity."""
    unique_email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    async with AsyncSessionLocal() as session:
        user = User(
            id=str(uuid.uuid4()),
            email=unique_email,
            hashed_password=get_password_hash("OldPassword@2026"),
            full_name="Password Test User",
            role=UserRole.MEMBER.value,
            is_active=True
        )
        session.add(user)
        await session.commit()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Wrong current password -> 400
        resp_bad = await ac.post("/api/v1/auth/change-password", headers=headers, json={
            "current_password": "WrongOldPassword",
            "new_password": "BrandNewPassword@2026"
        })
        assert resp_bad.status_code == 400
        
        # Correct current password, weak new password -> 400
        resp_weak = await ac.post("/api/v1/auth/change-password", headers=headers, json={
            "current_password": "OldPassword@2026",
            "new_password": "weak"
        })
        assert resp_weak.status_code == 422 or resp_weak.status_code == 400

        # Correct current password, strong new password -> 200
        resp_ok = await ac.post("/api/v1/auth/change-password", headers=headers, json={
            "current_password": "OldPassword@2026",
            "new_password": "NewStrongPassword@2026"
        })
        assert resp_ok.status_code == 200
        assert resp_ok.json()["success"] is True

# =========================================================================
# 2. OBJECT-LEVEL AUTHORIZATION & MULTI-TENANT ISOLATION (IDOR / BOLA)
# =========================================================================

@pytest.mark.asyncio
async def test_idor_cross_tenant_project_isolation():
    """
    CRITICAL IDOR / BOLA TEST:
    User A (Organization A, Project A) must NEVER access Project B of User B (Organization B).
    """
    async with AsyncSessionLocal() as session:
        # Create Tenant A
        user_a = User(
            id=str(uuid.uuid4()),
            email=f"user_a_{uuid.uuid4().hex[:6]}@tenant-a.com",
            hashed_password=get_password_hash("TenantA@2026"),
            full_name="Alice (Tenant A)",
            role=UserRole.PROJECT_OWNER.value,
            is_active=True
        )
        session.add(user_a)
        
        org_a = Organization(
            id=str(uuid.uuid4()),
            name="Tenant A Corp",
            slug=f"org-a-{uuid.uuid4().hex[:6]}",
            owner_id=user_a.id
        )
        session.add(org_a)
        
        ws_a = Workspace(
            id=str(uuid.uuid4()),
            name="Workspace A",
            organization_id=org_a.id
        )
        session.add(ws_a)
        
        proj_a = Project(
            id=str(uuid.uuid4()),
            name="Secret Initiative A",
            slug=f"secret-initiative-a-{uuid.uuid4().hex[:6]}",
            workspace_id=ws_a.id
        )
        session.add(proj_a)
        session.add(ProjectMember(
            id=str(uuid.uuid4()),
            project_id=proj_a.id,
            user_id=user_a.id,
            role=UserRole.PROJECT_OWNER.value
        ))

        # Create Tenant B
        user_b = User(
            id=str(uuid.uuid4()),
            email=f"user_b_{uuid.uuid4().hex[:6]}@tenant-b.com",
            hashed_password=get_password_hash("TenantB@2026"),
            full_name="Bob (Tenant B)",
            role=UserRole.PROJECT_OWNER.value,
            is_active=True
        )
        session.add(user_b)
        
        org_b = Organization(
            id=str(uuid.uuid4()),
            name="Tenant B Corp",
            slug=f"org-b-{uuid.uuid4().hex[:6]}",
            owner_id=user_b.id
        )
        session.add(org_b)
        
        ws_b = Workspace(
            id=str(uuid.uuid4()),
            name="Workspace B",
            organization_id=org_b.id
        )
        session.add(ws_b)
        
        proj_b = Project(
            id=str(uuid.uuid4()),
            name="Confidential Project B",
            slug=f"confidential-project-b-{uuid.uuid4().hex[:6]}",
            workspace_id=ws_b.id
        )
        session.add(proj_b)
        session.add(ProjectMember(
            id=str(uuid.uuid4()),
            project_id=proj_b.id,
            user_id=user_b.id,
            role=UserRole.PROJECT_OWNER.value
        ))

        # Add confidential document to Project B
        doc_b = Document(
            id=str(uuid.uuid4()),
            project_id=proj_b.id,
            filename="Confidential_Strategy_B.pdf",
            file_type="pdf",
            file_size=1024,
            storage_path="./uploads/fake.pdf",
            extracted_text="Tenant B confidential trade secrets",
            status="PROCESSED"
        )
        session.add(doc_b)

        await session.commit()

    token_a = create_access_token(user_a.id)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. User A tries to GET Project B details -> MUST BE FORBIDDEN (403)
        resp_proj = await ac.get(f"/api/v1/projects/{proj_b.id}", headers=headers_a)
        assert resp_proj.status_code == 403

        # 2. User A tries to list documents in Project B -> MUST BE FORBIDDEN (403)
        resp_docs = await ac.get(f"/api/v1/documents/project/{proj_b.id}", headers=headers_a)
        assert resp_docs.status_code == 403

        # 3. User A tries to GET specific document of Project B -> MUST BE FORBIDDEN (403)
        resp_single_doc = await ac.get(f"/api/v1/documents/{doc_b.id}", headers=headers_a)
        assert resp_single_doc.status_code == 403

        # 4. User A tries to generate architecture on Project B -> MUST BE FORBIDDEN (403)
        resp_arch = await ac.post(f"/api/v1/architecture/project/{proj_b.id}/generate", headers=headers_a)
        assert resp_arch.status_code == 403

        # 5. User A calls /api/v1/projects -> MUST ONLY CONTAIN Project A, NOT Project B
        resp_list = await ac.get("/api/v1/projects", headers=headers_a)
        assert resp_list.status_code == 200
        proj_ids_returned = [p["id"] for p in resp_list.json()["data"]]
        assert proj_a.id in proj_ids_returned
        assert proj_b.id not in proj_ids_returned

# =========================================================================
# 3. SSRF & URL INGESTION SECURITY TESTS
# =========================================================================

@pytest.mark.asyncio
async def test_ssrf_blocks_localhost_and_internal_ips():
    """Verify website ingestion blocks localhost, private IPs, and cloud metadata."""
    from app.documents.extractor import is_safe_url
    
    dangerous_urls = [
        "http://localhost:8000/api/v1/admin/metrics",
        "http://127.0.0.1:8000/api/v1/users",
        "http://127.0.0.1/admin",
        "http://0.0.0.0:8000",
        "http://10.0.0.1/internal-service",
        "http://192.168.1.1/router-admin",
        "http://172.16.0.1/private",
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "file:///etc/passwd",
        "ftp://ftp.internal.local",
        "gopher://127.0.0.1:70"
    ]
    
    for u in dangerous_urls:
        is_safe, reason = is_safe_url(u)
        assert is_safe is False, f"Expected {u} to be blocked by SSRF filter, but was allowed! Reason: {reason}"

@pytest.mark.asyncio
async def test_ssrf_api_endpoint_rejects_internal_urls():
    """Verify POST /api/v1/documents/ingest-url rejects SSRF payloads with 400 Bad Request."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        res_p = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = res_p.scalars().first()

    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/documents/ingest-url", headers=headers, json={
            "project_id": project.id,
            "url": "http://127.0.0.1:8000/api/v1/admin/metrics"
        })
        assert resp.status_code == 400
        assert "Security Block" in resp.json()["detail"] or "protocol" in resp.json()["detail"].lower()

# =========================================================================
# 4. FILE UPLOAD & SIGNATURE SECURITY TESTS
# =========================================================================

@pytest.mark.asyncio
async def test_file_upload_signature_validation():
    """Verify spoofed file extensions (e.g. executable with .pdf extension) are blocked."""
    from app.documents.extractor import validate_file_signature
    import tempfile
    
    # Create fake executable file named pdf
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00FakePEHeader")
        fake_pdf_path = f.name
        
    is_valid, err = validate_file_signature(fake_pdf_path, "pdf")
    assert is_valid is False
    assert "Invalid PDF" in err

    # Create real valid PDF header
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.7\nValid PDF Stream Header")
        valid_pdf_path = f.name
        
    is_valid_pdf, _ = validate_file_signature(valid_pdf_path, "pdf")
    assert is_valid_pdf is True

# =========================================================================
# 5. SECURITY HEADERS & CORS TESTS
# =========================================================================

@pytest.mark.asyncio
async def test_security_headers_present():
    """Verify modern HTTP security headers are attached to API responses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert "strict-origin" in resp.headers.get("Referrer-Policy", "").lower()
        assert resp.headers.get("Permissions-Policy") is not None

# =========================================================================
# 6. RATE LIMITING SECURITY TESTS
# =========================================================================

@pytest.mark.asyncio
async def test_rate_limiter_triggers_429():
    """Verify rate limiter triggers HTTP 429 after exceeding quota."""
    limiter.reset()
    key = "test_endpoint:127.0.0.1"
    
    # Allow 5 requests
    for _ in range(5):
        assert limiter.check_rate_limit(key, max_requests=5, window_seconds=60) is True
        
    # 6th request must be blocked
    assert limiter.check_rate_limit(key, max_requests=5, window_seconds=60) is False
    limiter.reset()
