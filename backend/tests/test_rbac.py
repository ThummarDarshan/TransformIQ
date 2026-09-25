import os
import sys
import pytest
import pytest_asyncio
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth.security import create_access_token
from app.models.user import User, UserRole
from app.models.project import Project
from app.config.database import AsyncSessionLocal
from sqlalchemy.future import select
from seed_rbac_demo import seed_rbac

@pytest.fixture(autouse=True, scope="module")
async def setup_rbac_data():
    await seed_rbac()

@pytest.mark.asyncio
async def test_unauthenticated_request_rejected():
    """Unauthenticated requests to protected endpoints must return 401 Unauthorized."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects")
        assert response.status_code == 401
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_invalid_jwt_rejected():
    """Invalid or forged JWT must return 401 Unauthorized."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": "Bearer invalid.fake.token"}
        response = await ac.get("/api/v1/projects", headers=headers)
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_access_allowed_for_admin():
    """Admin user can access /api/v1/admin/metrics."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        assert admin is not None
        
    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin/metrics", headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_admin_access_denied_for_viewer():
    """Viewer role must be denied access to /api/v1/admin/metrics with 403 Forbidden."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "viewer@transformiq.local"))
        viewer = res.scalars().first()
        assert viewer is not None
        
    token = create_access_token(viewer.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin/metrics", headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_viewer_cannot_save_architecture_layout():
    """Viewer cannot save architecture layout (requires ARCHITECTURE_EDIT). Returns 403."""
    async with AsyncSessionLocal() as session:
        res_v = await session.execute(select(User).filter(User.email == "viewer@transformiq.local"))
        viewer = res_v.scalars().first()
        res_p = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = res_p.scalars().first()
        
    token = create_access_token(viewer.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            f"/api/v1/architecture/project/{project.id}/save-layout",
            json=[{"id": "comp-1", "position": {"x": 100, "y": 200}}],
            headers=headers
        )
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_architect_can_save_architecture_layout():
    """Solution Architect has ARCHITECTURE_EDIT permission and can save layout."""
    async with AsyncSessionLocal() as session:
        res_a = await session.execute(select(User).filter(User.email == "architect@transformiq.local"))
        architect = res_a.scalars().first()
        res_p = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = res_p.scalars().first()
        
    token = create_access_token(architect.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            f"/api/v1/architecture/project/{project.id}/save-layout",
            json=[],
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_business_analyst_cannot_approve_blueprint():
    """Business Analyst cannot approve master blueprint (requires BLUEPRINT_APPROVE). Returns 403."""
    async with AsyncSessionLocal() as session:
        res_ba = await session.execute(select(User).filter(User.email == "analyst@transformiq.local"))
        analyst = res_ba.scalars().first()
        res_p = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = res_p.scalars().first()
        
    token = create_access_token(analyst.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            f"/api/v1/blueprints/project/{project.id}/approve",
            json={"action": "APPROVE", "comments": "Unauthorized approval attempt by BA"},
            headers=headers
        )
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_manager_can_approve_blueprint():
    """Manager has BLUEPRINT_APPROVE permission and can approve blueprint."""
    async with AsyncSessionLocal() as session:
        res_m = await session.execute(select(User).filter(User.email == "manager@transformiq.local"))
        manager = res_m.scalars().first()
        res_p = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = res_p.scalars().first()
        
    token = create_access_token(manager.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            f"/api/v1/blueprints/project/{project.id}/approve",
            json={"action": "APPROVE", "comments": "Approved by Executive Management"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"]["status"] == "APPROVED"

@pytest.mark.asyncio
async def test_member_cannot_manage_team():
    """Member role cannot invite/manage project members (requires TEAM_MANAGE). Returns 403."""
    async with AsyncSessionLocal() as session:
        res_mem = await session.execute(select(User).filter(User.email == "member@transformiq.local"))
        member = res_mem.scalars().first()
        res_p = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = res_p.scalars().first()
        
    token = create_access_token(member.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            f"/api/v1/projects/{project.id}/members",
            json={"email": "newbie@enterprise.com", "role": "MEMBER"},
            headers=headers
        )
        assert response.status_code == 403
