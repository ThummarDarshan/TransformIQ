import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.future import select

from app.main import app
from app.models.user import User, Organization, Workspace
from app.models.project import Project, ProjectStatus
from app.models.provenance import SourceEvidence, ArtifactProvenance, ProvenanceType, SourceType
from app.models.uncertainty import (
    RequirementUncertainty, UncertaintyCategory, UncertaintySeverity, UncertaintyStatus
)
from app.ai.uncertainty_analyzer import uncertainty_analyzer
from app.config.database import AsyncSessionLocal
from app.auth.security import create_access_token
from seed_rbac_demo import seed_rbac

@pytest.fixture(autouse=True, scope="module")
async def setup_data():
    await seed_rbac()

@pytest.fixture
async def test_auth_context():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).filter(User.email == "admin@transformiq.local"))
        admin = res.scalars().first()
        proj_res = await db.execute(select(Project).filter(Project.slug == "customer-complaint-transformation"))
        project = proj_res.scalars().first()
        ev_res = await db.execute(select(SourceEvidence).filter(SourceEvidence.project_id == project.id))
        ev1 = ev_res.scalars().first()

        token = create_access_token(admin.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        return {
            "user": admin,
            "project": project,
            "evidence": ev1,
            "headers": headers,
            "token": token
        }

@pytest.mark.asyncio
async def test_uncertainty_analyzer_detects_missing_eligibility_rule(test_auth_context):
    """Test 1: Analyzer identifies missing eligibility criteria when automation is mandated."""
    project = test_auth_context["project"]
    ev = test_auth_context["evidence"]
    
    uncertainties = uncertainty_analyzer.analyze_source_material(
        project_id=project.id,
        project_name=project.name,
        industry=project.industry,
        business_problem=project.business_problem,
        business_objective=project.business_objective,
        source_evidences=[ev],
        existing_uncertainties=[]
    )
    
    assert len(uncertainties) >= 3
    # Check that Claim / Automation Eligibility Threshold is flagged
    eligibility_item = next((u for u in uncertainties if "Eligibility" in u["title"] or "Approval" in u["title"]), None)
    assert eligibility_item is not None
    assert eligibility_item["category"] == UncertaintyCategory.BUSINESS_RULE.value
    assert eligibility_item["severity"] == UncertaintySeverity.HIGH.value
    assert eligibility_item["is_high_risk_assumption"] is True
    assert "criteria" in eligibility_item["what_to_confirm"].lower() or "approval" in eligibility_item["what_to_confirm"].lower()

@pytest.mark.asyncio
async def test_uncertainty_analyzer_detects_contradiction():
    """Test 2: Contradiction detection when source material conflicts on manual vs zero-touch."""
    conflict_evs = [
        SourceEvidence(
            id=str(uuid.uuid4()),
            project_id="proj-conflict",
            source_code="SRC-A",
            document_name="Policy_A.pdf",
            page_number=1,
            section_heading="Rules",
            exact_text="All decision outputs require mandatory manual review and specialist sign-off."
        ),
        SourceEvidence(
            id=str(uuid.uuid4()),
            project_id="proj-conflict",
            source_code="SRC-B",
            document_name="Policy_B.pdf",
            page_number=3,
            section_heading="Vision",
            exact_text="System mandates 100% zero-touch automated processing without human intervention."
        )
    ]
    
    uncertainties = uncertainty_analyzer.analyze_source_material(
        project_id="proj-conflict",
        project_name="Conflict Project",
        industry="Finance",
        business_problem="Conflicting manual review vs automated processing statements.",
        business_objective="Resolve workflow",
        source_evidences=conflict_evs,
        existing_uncertainties=[]
    )
    
    contradiction_item = next((u for u in uncertainties if "Conflicting" in u["title"] or "Contradictory" in u["title"]), None)
    assert contradiction_item is not None
    assert contradiction_item["severity"] == UncertaintySeverity.CRITICAL.value
    assert contradiction_item["category"] == UncertaintyCategory.WORKFLOW.value

@pytest.mark.asyncio
async def test_get_project_uncertainties_api_auto_synthesizes(test_auth_context):
    """Test 3: GET /uncertainties/project/{id} auto-generates and persists uncertainties if empty."""
    headers = test_auth_context["headers"]
    project = test_auth_context["project"]
    
    # Clean up project uncertainties to test clean synthesis
    async with AsyncSessionLocal() as db:
        await db.execute(delete(RequirementUncertainty).filter(RequirementUncertainty.project_id == project.id))
        await db.commit()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["project_id"] == project.id
    assert len(data["uncertainties"]) >= 3
    assert data["stats"]["total_count"] >= 3
    assert data["stats"]["unconfirmed_count"] >= 3
    
    # Check first item fields
    first = data["uncertainties"][0]
    assert "what_is_unclear" in first
    assert "assumption" in first
    assert "what_to_confirm" in first
    assert "potential_impact" in first
    assert first["status"] == "UNCONFIRMED"

@pytest.mark.asyncio
async def test_user_confirmation_workflow(test_auth_context):
    """Test 4: User confirms an uncertainty with business rule clarification."""
    headers = test_auth_context["headers"]
    project = test_auth_context["project"]
    
    # 1. Fetch uncertainties
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        list_res = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        uncertainty_id = list_res.json()["data"]["uncertainties"][0]["id"]
        
        # 2. Confirm clarification
        clarification_text = "All claims under $1,000 auto-approved; all claims >= $1,000 require Senior Claims Specialist approval."
        confirm_res = await ac.post(
            f"/api/v1/uncertainties/{uncertainty_id}/confirm",
            headers=headers,
            json={"user_clarification": clarification_text}
        )
        
        assert confirm_res.status_code == 200
        confirm_data = confirm_res.json()["data"]
        assert confirm_data["status"] == "CONFIRMED"
        assert confirm_data["user_clarification"] == clarification_text
        
        # 3. Verify in list
        updated_list = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        stats = updated_list.json()["data"]["stats"]
        assert stats["confirmed_count"] == 1

@pytest.mark.asyncio
async def test_edit_and_accept_assumption_workflow(test_auth_context):
    """Test 5: User accepts or modifies stated AI assumption."""
    headers = test_auth_context["headers"]
    project = test_auth_context["project"]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        list_res = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        items = list_res.json()["data"]["uncertainties"]
        target_item = items[1] # second item
        
        edit_res = await ac.post(
            f"/api/v1/uncertainties/{target_item['id']}/edit-assumption",
            headers=headers,
            json={
                "assumption": "4-tier RBAC (Client, Claims Specialist, Manager, SuperAdmin)",
                "user_clarification": "Accepted 4-tier RBAC schema."
            }
        )
        
        assert edit_res.status_code == 200
        assert edit_res.json()["data"]["status"] == "RESOLVED"

@pytest.mark.asyncio
async def test_reject_uncertainty_workflow(test_auth_context):
    """Test 6: User dismisses / rejects an uncertainty as non-applicable."""
    headers = test_auth_context["headers"]
    project = test_auth_context["project"]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        list_res = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        target_item = list_res.json()["data"]["uncertainties"][-1]
        
        reject_res = await ac.post(
            f"/api/v1/uncertainties/{target_item['id']}/reject",
            headers=headers,
            json={"reason": "Out of scope for Phase 1"}
        )
        
        assert reject_res.status_code == 200
        assert reject_res.json()["data"]["status"] == "REJECTED"

@pytest.mark.asyncio
async def test_confirmed_clarification_enters_blueprint_payload(test_auth_context):
    """Test 7: Confirmed user clarifications feed into Master Blueprint payload."""
    headers = test_auth_context["headers"]
    project = test_auth_context["project"]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Fetch uncertainties and confirm one
        list_res = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        u_id = list_res.json()["data"]["uncertainties"][0]["id"]
        
        await ac.post(
            f"/api/v1/uncertainties/{u_id}/confirm",
            headers=headers,
            json={"user_clarification": "Tier 1: < $500 auto-approved, Tier 2: $500-$5000 specialist review."}
        )
        
        # 2. Fetch Blueprint
        bp_res = await ac.get(f"/api/v1/blueprints/project/{project.id}", headers=headers)
        assert bp_res.status_code == 200
        bp_data = bp_res.json()["data"]
        
        # Check what_i_couldnt_figure_out section
        assert "what_i_couldnt_figure_out" in bp_data
        assert bp_data["what_i_couldnt_figure_out"]["confirmed_count"] >= 1
        
        # Check confirmed_clarifications in blueprint
        assert "confirmed_clarifications" in bp_data
        assert len(bp_data["confirmed_clarifications"]) >= 1
        assert any("Tier 1" in c["clarification"] for c in bp_data["confirmed_clarifications"])

@pytest.mark.asyncio
async def test_re_analyze_preserves_confirmed_items(test_auth_context):
    """Test 8: Re-running analysis does NOT overwrite or re-ask confirmed items."""
    headers = test_auth_context["headers"]
    project = test_auth_context["project"]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Confirm an item
        list_res = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        first_item = list_res.json()["data"]["uncertainties"][0]
        
        await ac.post(
            f"/api/v1/uncertainties/{first_item['id']}/confirm",
            headers=headers,
            json={"user_clarification": "Confirmed user roles: Admin & Reviewer."}
        )
        
        # 2. Trigger re-analysis
        analyze_res = await ac.post(f"/api/v1/uncertainties/project/{project.id}/analyze", headers=headers)
        assert analyze_res.status_code == 200
        
        # 3. Verify confirmed item is preserved
        refetched = await ac.get(f"/api/v1/uncertainties/project/{project.id}", headers=headers)
        matched = next((it for it in refetched.json()["data"]["uncertainties"] if it["id"] == first_item["id"]), None)
        assert matched is not None
        assert matched["status"] == "CONFIRMED"
        assert matched["user_clarification"] == "Confirmed user roles: Admin & Reviewer."
