import pytest
import httpx
from app.main import app
from app.config.database import engine, Base, AsyncSessionLocal
from app.seed.demo_data import seed_database

@pytest.fixture(autouse=True, scope="module")
def setup_db():
    pass

@pytest.mark.asyncio
async def test_root_and_health():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_database(session)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "TransformIQ" in data["product"]
        assert data["status"] == "HEALTHY"

@pytest.mark.asyncio
async def test_login_and_projects():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@transformiq.local",
            "password": "TransformIQ@2026"
        })
        if login_resp.status_code != 200:
            login_resp = await client.post("/api/v1/auth/login", json={
                "email": "demo@transformiq.ai",
                "password": "Demo@12345"
            })
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # List projects
        proj_resp = await client.get("/api/v1/projects", headers=headers)
        assert proj_resp.status_code == 200
        assert len(proj_resp.json()["data"]) > 0

@pytest.mark.asyncio
async def test_what_if_simulation():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@transformiq.local",
            "password": "TransformIQ@2026"
        })
        if login_resp.status_code != 200:
            login_resp = await client.post("/api/v1/auth/login", json={
                "email": "demo@transformiq.ai",
                "password": "Demo@12345"
            })
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.get("/api/v1/projects", headers=headers)
        assert proj_resp.status_code == 200
        projects = proj_resp.json()["data"]
        assert len(projects) > 0
        project_id = projects[0]["id"]
        
        sim_resp = await client.post(
            f"/api/v1/simulations/project/{project_id}/run",
            headers=headers,
            json={
                "automation_level": 80,
                "team_size": 7,
                "budget": 160000.0,
                "timeline_months": 4,
                "ai_adoption_level": "HIGH"
            }
        )
        assert sim_resp.status_code == 200
        sim_data = sim_resp.json()["data"]
        assert "expected_roi_percentage" in sim_data
        assert sim_data["automation_level"] == 80

@pytest.mark.asyncio
async def test_default_project_alias():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@transformiq.local",
            "password": "TransformIQ@2026"
        })
        if login_resp.status_code != 200:
            login_resp = await client.post("/api/v1/auth/login", json={
                "email": "demo@transformiq.ai",
                "password": "Demo@12345"
            })
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request default project
        resp = await client.get("/api/v1/projects/default", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["id"] is not None
        assert data["data"]["id"] != "default"

@pytest.mark.asyncio
async def test_default_project_stages():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@transformiq.local",
            "password": "TransformIQ@2026"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test Discovery with 'default'
        disc_resp = await client.get("/api/v1/discovery/project/default/questions", headers=headers)
        assert disc_resp.status_code == 200
        assert disc_resp.json()["success"] is True

        # Test Gaps with 'default'
        gaps_resp = await client.get("/api/v1/gaps/project/default", headers=headers)
        assert gaps_resp.status_code == 200
        assert gaps_resp.json()["success"] is True

        # Test Recommendations with 'default'
        rec_resp = await client.get("/api/v1/recommendations/project/default", headers=headers)
        assert rec_resp.status_code == 200
        assert rec_resp.json()["success"] is True

        # Test Architecture with 'default'
        arch_resp = await client.get("/api/v1/architecture/project/default", headers=headers)
        assert arch_resp.status_code == 200
        assert arch_resp.json()["success"] is True

        # Test Collaboration Comments with 'default'
        comm_resp = await client.get("/api/v1/collaboration/project/default/comments", headers=headers)
        assert comm_resp.status_code == 200
        assert comm_resp.json()["success"] is True

        # Post Comment with 'default'
        post_comm = await client.post(
            "/api/v1/collaboration/project/default/comments",
            headers=headers,
            json={
                "section": "architecture",
                "content": "Automated verification test comment.",
                "mentions": ["@LeadArchitect"]
            }
        )
        assert post_comm.status_code == 200
        assert post_comm.json()["success"] is True
        assert post_comm.json()["data"]["content"] == "Automated verification test comment."

        # Test Planning with 'default'
        plan_resp = await client.get("/api/v1/planning/project/default", headers=headers)
        assert plan_resp.status_code == 200
        plan_data = plan_resp.json()
        assert plan_data["success"] is True
        assert "roadmap" in plan_data["data"]
        assert "phases" in plan_data["data"]["roadmap"]
        assert "estimate" in plan_data["data"]
        assert "total_estimated_hours" in plan_data["data"]["estimate"]

        # Test Planning generate with 'default'
        gen_plan = await client.post("/api/v1/planning/project/default/generate", headers=headers)
        assert gen_plan.status_code == 200
        gen_data = gen_plan.json()
        assert gen_data["success"] is True
        assert "roadmap" in gen_data["data"]
        assert "estimate" in gen_data["data"]

        # Test Discovery Chat with 'default'
        chat_resp = await client.post(
            "/api/v1/discovery/project/default/chat",
            headers=headers,
            json={
                "message": "What is the recommended architecture for this project?",
                "language": "en"
            }
        )
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()
        assert chat_data["success"] is True
        assert "message" in chat_data["data"]
        assert len(chat_data["data"]["message"]) > 0
        assert "reply" in chat_data["data"]
        assert "suggested_actions" in chat_data["data"]
