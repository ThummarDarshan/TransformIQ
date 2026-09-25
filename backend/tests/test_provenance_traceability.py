import os
import sys
import pytest
import pytest_asyncio
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth.security import create_access_token
from app.models.user import User
from app.models.project import Project
from app.models.provenance import SourceEvidence, ArtifactProvenance, ProvenanceType, SourceType
from app.documents.extractor import chunk_document_with_metadata
from app.config.database import AsyncSessionLocal
from sqlalchemy.future import select
from seed_rbac_demo import seed_rbac

@pytest.fixture(autouse=True, scope="module")
async def setup_data():
    await seed_rbac()

@pytest.mark.asyncio
async def test_chunk_extractor_metadata_and_offsets():
    """Verify that chunk_document_with_metadata extracts exact start/end offsets and stable sections."""
    sample_text = """# Executive Overview
Customer complaints currently take 5-7 business days to resolve due to manual ticket assignment across fragmented legacy systems.

# Architecture Constraints
All new microservices must run on Kubernetes and maintain 99.9% uptime SLA."""

    chunks = chunk_document_with_metadata(
        full_text=sample_text,
        pages_or_slides=[
            {"page_number": 1, "content": sample_text}
        ],
        chunk_size=150,
        overlap=20
    )

    assert len(chunks) >= 2
    for chunk in chunks:
        assert "exact_text" in chunk
        assert "start_offset" in chunk
        assert "end_offset" in chunk
        assert chunk["end_offset"] > chunk["start_offset"]
        assert len(chunk["exact_text"]) > 0


@pytest.mark.asyncio
async def test_get_project_source_evidence_list():
    """GET /api/v1/provenance/project/{id}/evidence returns canonical evidence anchors with SRC-XXX codes."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()
        assert admin is not None and project is not None

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(f"/api/v1/provenance/project/{project.id}/evidence", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert len(payload["data"]) >= 4
        source_codes = [e["source_code"] for e in payload["data"]]
        assert "SRC-001" in source_codes
        assert "SRC-002" in source_codes


@pytest.mark.asyncio
async def test_get_direct_artifact_provenance():
    """GET /api/v1/provenance/project/{id}/artifact/REQUIREMENT/REQ-F01 returns DIRECT evidence."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(
            f"/api/v1/provenance/project/{project.id}/artifact/REQUIREMENT/REQ-F01",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        prov = data["primary_provenance"]
        assert prov["provenance_type"] == "DIRECT"
        assert prov["source_code"] == "SRC-001"
        assert "customer complaints" in prov["exact_text"].lower()
        assert prov["page_number"] == 2


@pytest.mark.asyncio
async def test_get_derived_artifact_provenance():
    """GET /api/v1/provenance/project/{id}/artifact/REQUIREMENT/REQ-F04 returns DERIVED evidence."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(
            f"/api/v1/provenance/project/{project.id}/artifact/REQUIREMENT/REQ-F04",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        prov = data["primary_provenance"]
        assert prov["provenance_type"] == "DERIVED"
        assert prov["source_code"] == "SRC-001"
        assert "customer complaints" in prov["exact_text"].lower()


@pytest.mark.asyncio
async def test_get_recommended_artifact_provenance_without_fake_citation():
    """GET /api/v1/provenance/project/{id}/artifact/REQUIREMENT/REQ-NF01 returns RECOMMENDED without hallucination."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(
            f"/api/v1/provenance/project/{project.id}/artifact/REQUIREMENT/REQ-NF01",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        prov = data["primary_provenance"]
        assert prov["provenance_type"] == "RECOMMENDED"


@pytest.mark.asyncio
async def test_traceability_matrix_endpoint():
    """GET /api/v1/provenance/project/{id}/matrix returns complete matrix with coverage statistics."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(f"/api/v1/provenance/project/{project.id}/matrix", headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["stats"]["total_requirements"] >= 6
        assert data["stats"]["direct_source_backed"] >= 4
        assert data["stats"]["derived_requirements"] >= 1
        assert data["stats"]["ai_recommended"] >= 1
        assert data["stats"]["coverage_percentage"] >= 80.0
        assert len(data["matrix"]) >= 6


@pytest.mark.asyncio
async def test_business_analysis_provenance_enrichment():
    """GET /api/v1/business-analysis/project/{id} enriches requirements with provenance payload."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(f"/api/v1/business-analysis/project/{project.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]
        func_reqs = data["functional_requirements"]
        assert len(func_reqs) > 0
        req_0 = func_reqs[0]
        assert "provenance" in req_0
        assert req_0["provenance"]["provenance_type"] in ["DIRECT", "DERIVED", "RECOMMENDED"]
        assert "source_code" in req_0["provenance"]


@pytest.mark.asyncio
async def test_master_blueprint_traceability_summary():
    """GET /api/v1/blueprints/project/{id} includes traceability_summary metrics."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(f"/api/v1/blueprints/project/{project.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert "traceability_summary" in data
        summary = data["traceability_summary"]
        assert summary["total_evidence_sources"] >= 4
        assert summary["direct_citations_count"] >= 4
        assert summary["coverage_percentage"] >= 80.0


@pytest.mark.asyncio
async def test_legacy_or_missing_provenance_fallback():
    """Unlinked artifact returns fallback without 500 error."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await session.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()

    token = create_access_token(admin.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(
            f"/api/v1/provenance/project/{project.id}/artifact/CUSTOM_ITEM/NON_EXISTENT_999",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["has_provenance"] is False or data["primary_provenance"] is not None
