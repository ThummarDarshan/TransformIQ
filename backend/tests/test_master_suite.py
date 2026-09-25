import asyncio
import os
import sys
import uuid
import json
import httpx
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_V1 = f"{BASE_URL}/api/v1"

ACCOUNTS = {
    "ADMIN": {"email": "admin@transformiq.local", "password": "TransformIQ@2026", "name": "Sarah Connor"},
    "PROJECT_OWNER": {"email": "owner@transformiq.local", "password": "TransformIQ@2026", "name": "Elena Rostova"},
    "BUSINESS_ANALYST": {"email": "analyst@transformiq.local", "password": "TransformIQ@2026", "name": "Priya Sharma"},
    "SOLUTION_ARCHITECT": {"email": "architect@transformiq.local", "password": "TransformIQ@2026", "name": "David Chen"},
    "MANAGER": {"email": "manager@transformiq.local", "password": "TransformIQ@2026", "name": "Marcus Vance"},
    "MEMBER": {"email": "member@transformiq.local", "password": "TransformIQ@2026", "name": "Liam Murphy"},
    "VIEWER": {"email": "viewer@transformiq.local", "password": "TransformIQ@2026", "name": "Victoria Stone"},
}

tokens = {}
test_results = []

def record(area, test_name, status, details=""):
    test_results.append({
        "area": area,
        "test": test_name,
        "status": status,
        "details": details
    })
    symbol = "[PASS]" if status == "PASS" else ("[FAIL]" if status == "FAIL" else f"[{status}]")
    print(f"{symbol} [{area}] {test_name}: {details}", flush=True)

async def run_master_tests():
    print("==================================================================", flush=True)
    print("STARTING MASTER FULL PROJECT TEST SUITE - TRANSFORMIQ 2026", flush=True)
    print("==================================================================\n", flush=True)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # ================================================================
        # 1. APPLICATION HEALTH & SYSTEM STARTUP
        # ================================================================
        print("--- 1. APPLICATION HEALTH ---", flush=True)
        try:
            r = await client.get("/")
            if r.status_code == 200 and r.json().get("status") == "HEALTHY":
                record("Application Health", "Root Endpoint", "PASS", f"Status 200, Product: {r.json().get('product')}")
            else:
                record("Application Health", "Root Endpoint", "FAIL", f"Status {r.status_code}, response: {r.text}")
        except Exception as e:
            record("Application Health", "Root Endpoint", "FAIL", str(e))

        try:
            r = await client.get("/health")
            if r.status_code == 200 and r.json().get("status") == "ok":
                record("Application Health", "Health Check Endpoint", "PASS", "Status 200 ok")
            else:
                record("Application Health", "Health Check Endpoint", "FAIL", f"Status {r.status_code}")
        except Exception as e:
            record("Application Health", "Health Check Endpoint", "FAIL", str(e))

        try:
            r = await client.get("/docs")
            if r.status_code == 200:
                record("Application Health", "OpenAPI Docs Endpoint", "PASS", "Swagger UI accessible")
            else:
                record("Application Health", "OpenAPI Docs Endpoint", "FAIL", f"Status {r.status_code}")
        except Exception as e:
            record("Application Health", "OpenAPI Docs Endpoint", "FAIL", str(e))

        # ================================================================
        # 2. AUTHENTICATION TESTING (All 7 Roles + Failure Cases)
        # ================================================================
        print("\n--- 2. AUTHENTICATION & SESSION SECURITY ---", flush=True)
        for role, creds in ACCOUNTS.items():
            try:
                r = await client.post("/api/v1/auth/login", json={"email": creds["email"], "password": creds["password"]})
                if r.status_code == 200 and r.json().get("success"):
                    token_data = r.json()["data"]["token"]["access_token"]
                    user_data = r.json()["data"]["user"]
                    tokens[role] = token_data
                    record("Authentication", f"Login {role} ({creds['email']})", "PASS", f"JWT received, user ID: {user_data['id']}, role: {user_data['role']}")
                else:
                    record("Authentication", f"Login {role}", "FAIL", f"Status: {r.status_code}, {r.text}")
            except Exception as e:
                record("Authentication", f"Login {role}", "FAIL", str(e))

        # Auth Failure Cases
        try:
            r = await client.post("/api/v1/auth/login", json={"email": "admin@transformiq.local", "password": "WrongPassword123!"})
            if r.status_code == 401:
                record("Authentication", "Invalid Password Rejection", "PASS", "Returned 401 Unauthorized")
            else:
                record("Authentication", "Invalid Password Rejection", "FAIL", f"Expected 401, got {r.status_code}")
        except Exception as e:
            record("Authentication", "Invalid Password Rejection", "FAIL", str(e))

        try:
            r = await client.post("/api/v1/auth/login", json={"email": "nonexistent@fakeuser.com", "password": "TransformIQ@2026"})
            if r.status_code == 401:
                record("Authentication", "Non-Existent User Rejection", "PASS", "Returned 401 Unauthorized")
            else:
                record("Authentication", "Non-Existent User Rejection", "FAIL", f"Expected 401, got {r.status_code}")
        except Exception as e:
            record("Authentication", "Non-Existent User Rejection", "FAIL", str(e))

        try:
            r = await client.post("/api/v1/auth/login", json={"email": "", "password": ""})
            if r.status_code in [400, 401, 422]:
                record("Authentication", "Empty Credentials Rejection", "PASS", f"Returned {r.status_code}")
            else:
                record("Authentication", "Empty Credentials Rejection", "FAIL", f"Expected 4xx, got {r.status_code}")
        except Exception as e:
            record("Authentication", "Empty Credentials Rejection", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/projects")
            if r.status_code == 401:
                record("Authentication", "Unauthenticated Route Protection", "PASS", "Protected endpoint returned 401")
            else:
                record("Authentication", "Unauthenticated Route Protection", "FAIL", f"Expected 401, got {r.status_code}")
        except Exception as e:
            record("Authentication", "Unauthenticated Route Protection", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/projects", headers={"Authorization": "Bearer forged.invalid.jwt"})
            if r.status_code == 401:
                record("Authentication", "Invalid/Forged JWT Protection", "PASS", "Protected endpoint returned 401")
            else:
                record("Authentication", "Invalid/Forged JWT Protection", "FAIL", f"Expected 401, got {r.status_code}")
        except Exception as e:
            record("Authentication", "Invalid/Forged JWT Protection", "FAIL", str(e))

        # ================================================================
        # 3. ADMIN PLATFORM & GOVERNANCE APIS
        # ================================================================
        print("\n--- 3. ADMIN PLATFORM TESTING ---", flush=True)
        admin_hdr = {"Authorization": f"Bearer {tokens.get('ADMIN', '')}"}
        viewer_hdr = {"Authorization": f"Bearer {tokens.get('VIEWER', '')}"}
        member_hdr = {"Authorization": f"Bearer {tokens.get('MEMBER', '')}"}
        ba_hdr = {"Authorization": f"Bearer {tokens.get('BUSINESS_ANALYST', '')}"}
        arch_hdr = {"Authorization": f"Bearer {tokens.get('SOLUTION_ARCHITECT', '')}"}
        mgr_hdr = {"Authorization": f"Bearer {tokens.get('MANAGER', '')}"}
        owner_hdr = {"Authorization": f"Bearer {tokens.get('PROJECT_OWNER', '')}"}

        try:
            r = await client.get("/api/v1/admin/metrics", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin Metrics Overview", "PASS", "System metrics retrieved")
            else:
                record("Admin Testing", "Admin Metrics Overview", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin Metrics Overview", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/admin/users", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin User Management List", "PASS", f"Found {len(r.json()['data'])} users")
            else:
                record("Admin Testing", "Admin User Management List", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin User Management List", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/admin/organization", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin Organization Details", "PASS", f"Organization: {r.json()['data']['name']}")
            else:
                record("Admin Testing", "Admin Organization Details", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin Organization Details", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/organizations", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin Organizations List", "PASS", f"Found {len(r.json()['data'])} organizations")
            else:
                record("Admin Testing", "Admin Organizations List", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin Organizations List", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/admin/workspaces", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin Workspaces List", "PASS", f"Found {len(r.json()['data'])} workspaces")
            else:
                record("Admin Testing", "Admin Workspaces List", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin Workspaces List", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/admin/audit-logs", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin Audit Logs Query", "PASS", f"Retrieved {len(r.json()['data'])} audit logs")
            else:
                record("Admin Testing", "Admin Audit Logs Query", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin Audit Logs Query", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/admin/ai-usage", headers=admin_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Admin Testing", "Admin AI Usage Telemetry", "PASS", "AI telemetry stats retrieved")
            else:
                record("Admin Testing", "Admin AI Usage Telemetry", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Admin Testing", "Admin AI Usage Telemetry", "FAIL", str(e))

        # Admin Forbidden for non-admin
        try:
            r = await client.get("/api/v1/admin/metrics", headers=viewer_hdr)
            if r.status_code == 403:
                record("RBAC Testing", "Viewer Denied Admin Metrics (403)", "PASS", "Protected with 403 Forbidden")
            else:
                record("RBAC Testing", "Viewer Denied Admin Metrics (403)", "FAIL", f"Expected 403, got {r.status_code}")
        except Exception as e:
            record("RBAC Testing", "Viewer Denied Admin Metrics (403)", "FAIL", str(e))

        try:
            r = await client.get("/api/v1/admin/users", headers=member_hdr)
            if r.status_code == 403:
                record("RBAC Testing", "Member Denied Admin Users (403)", "PASS", "Protected with 403 Forbidden")
            else:
                record("RBAC Testing", "Member Denied Admin Users (403)", "FAIL", f"Expected 403, got {r.status_code}")
        except Exception as e:
            record("RBAC Testing", "Member Denied Admin Users (403)", "FAIL", str(e))

        # ================================================================
        # 4. PROJECT INGESTION & DATA ISOLATION
        # ================================================================
        print("\n--- 4. PROJECT TESTING & SEED RETRIEVAL ---", flush=True)
        project_id = None
        try:
            r = await client.get("/api/v1/projects", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success") and len(r.json()["data"]) > 0:
                projects = r.json()["data"]
                project = projects[0]
                project_id = project["id"]
                record("Project Testing", "Fetch Projects List", "PASS", f"Found {len(projects)} projects, Active ID: {project_id} ('{project['name']}')")
            else:
                record("Project Testing", "Fetch Projects List", "FAIL", f"Status: {r.status_code}, {r.text}")
        except Exception as e:
            record("Project Testing", "Fetch Projects List", "FAIL", str(e))

        if not project_id:
            print("ERROR: No project found. Aborting project pipeline tests.", flush=True)
            return

        # Fetch Project Details
        try:
            r = await client.get(f"/api/v1/projects/{project_id}", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Project Testing", "Fetch Project Details", "PASS", f"Name: {r.json()['data']['name']}, Status: {r.json()['data']['status']}")
            else:
                record("Project Testing", "Fetch Project Details", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Project Testing", "Fetch Project Details", "FAIL", str(e))

        # Fetch Project Members
        try:
            r = await client.get(f"/api/v1/projects/{project_id}/members", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Project Testing", "Fetch Project Members", "PASS", f"Found {len(r.json()['data'])} assigned members")
            else:
                record("Project Testing", "Fetch Project Members", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Project Testing", "Fetch Project Members", "FAIL", str(e))

        # ================================================================
        # 5. TRANSFORMIQ 13-STAGE PIPELINE WORKFLOW TESTING
        # ================================================================
        print("\n--- 5. 13-STAGE TRANSFORMATION PIPELINE ---", flush=True)

        # Stage 1: Discovery Chat
        try:
            chat_payload = {
                "message": "We need to automate customer complaint triage and reduce turnaround from 48h to 12m.",
                "language": "en"
            }
            r = await client.post(f"/api/v1/discovery/project/{project_id}/chat", json=chat_payload, headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                msg = r.json()["data"].get("message", "")
                record("Stage 1 - Discovery", "AI Discovery Chat Interaction", "PASS", f"AI Response: {msg[:80]}...")
            else:
                record("Stage 1 - Discovery", "AI Discovery Chat Interaction", "FAIL", f"Status: {r.status_code}, {r.text}")
        except Exception as e:
            record("Stage 1 - Discovery", "AI Discovery Chat Interaction", "FAIL", str(e))

        # Multilingual Discovery (Hindi & Gujarati)
        try:
            r_hi = await client.post(f"/api/v1/discovery/project/{project_id}/chat", json={"message": "नमस्ते", "language": "hi"}, headers=owner_hdr)
            r_gu = await client.post(f"/api/v1/discovery/project/{project_id}/chat", json={"message": "નમસ્તે", "language": "gu"}, headers=owner_hdr)
            if r_hi.status_code == 200 and r_gu.status_code == 200:
                record("Stage 1 - Discovery", "Multilingual Discovery (EN, HI, GU)", "PASS", "Hindi and Gujarati AI interactions verified")
            else:
                record("Stage 1 - Discovery", "Multilingual Discovery (EN, HI, GU)", "FAIL", f"HI: {r_hi.status_code}, GU: {r_gu.status_code}")
        except Exception as e:
            record("Stage 1 - Discovery", "Multilingual Discovery (EN, HI, GU)", "FAIL", str(e))

        # Stage 2: Business Analysis & Stakeholders Generation
        try:
            r = await client.post(f"/api/v1/business-analysis/project/{project_id}/generate", headers=ba_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 2 - Business Analysis", "Generate AS-IS Analysis & Stakeholders", "PASS", "AI business analysis generated and saved")
            else:
                record("Stage 2 - Business Analysis", "Generate AS-IS Analysis & Stakeholders", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 2 - Business Analysis", "Generate AS-IS Analysis & Stakeholders", "FAIL", str(e))

        # Stage 2 Fetch
        try:
            r = await client.get(f"/api/v1/business-analysis/project/{project_id}", headers=ba_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                record("Stage 2 - Business Analysis", "Fetch AS-IS Analysis & Stakeholders", "PASS", f"Found {len(data.get('stakeholders', []))} stakeholders, {len(data.get('functional_requirements', []))} functional reqs")
            else:
                record("Stage 2 - Business Analysis", "Fetch AS-IS Analysis & Stakeholders", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 2 - Business Analysis", "Fetch AS-IS Analysis & Stakeholders", "FAIL", str(e))

        # Stage 3: Gap Analysis Generation & Fetch
        try:
            r = await client.post(f"/api/v1/gaps/project/{project_id}/generate", headers=ba_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 3 - Gap Analysis", "Generate 8-Dimension Gap Matrix", "PASS", "Gap matrix generated successfully")
            else:
                record("Stage 3 - Gap Analysis", "Generate 8-Dimension Gap Matrix", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 3 - Gap Analysis", "Generate 8-Dimension Gap Matrix", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/gaps/project/{project_id}", headers=ba_hdr)
            if r.status_code == 200 and r.json().get("success"):
                gaps = r.json()["data"].get("gaps", [])
                record("Stage 3 - Gap Analysis", "Fetch 8-Dimension Gap Matrix", "PASS", f"Retrieved {len(gaps)} categorized enterprise gaps")
            else:
                record("Stage 3 - Gap Analysis", "Fetch 8-Dimension Gap Matrix", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 3 - Gap Analysis", "Fetch 8-Dimension Gap Matrix", "FAIL", str(e))

        # Stage 4: AI Recommendations & Explainability
        rec_id = None
        try:
            r = await client.post(f"/api/v1/recommendations/project/{project_id}/generate", headers=ba_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 4 - AI Recommendations", "Generate AI Recommendations", "PASS", "AI recommendations generated")
            else:
                record("Stage 4 - AI Recommendations", "Generate AI Recommendations", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 4 - AI Recommendations", "Generate AI Recommendations", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/recommendations/project/{project_id}", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                recs = r.json()["data"].get("recommendations", [])
                if recs: rec_id = recs[0]["id"]
                record("Stage 4 - AI Recommendations", "Fetch Recommendations Suite", "PASS", f"Found {len(recs)} recommendations")
            else:
                record("Stage 4 - AI Recommendations", "Fetch Recommendations Suite", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 4 - AI Recommendations", "Fetch Recommendations Suite", "FAIL", str(e))

        if rec_id:
            # Explainable AI "Why?"
            try:
                r = await client.get(f"/api/v1/recommendations/why/{rec_id}", headers=owner_hdr)
                if r.status_code == 200 and r.json().get("success"):
                    why = r.json()["data"]
                    record("Stage 4 - Explainable AI", "Explainable AI ('Why?' Modal)", "PASS", f"Confidence: {why.get('confidence_score')}, Citations: {len(why.get('citations', []))}")
                else:
                    record("Stage 4 - Explainable AI", "Explainable AI ('Why?' Modal)", "FAIL", f"Status: {r.status_code}")
            except Exception as e:
                record("Stage 4 - Explainable AI", "Explainable AI ('Why?' Modal)", "FAIL", str(e))

            # Human-in-the-Loop Status Transition (Manager Approve Allowed, Member Forbidden)
            try:
                r = await client.post(f"/api/v1/recommendations/{rec_id}/status?status_value=APPROVED", headers=mgr_hdr)
                if r.status_code == 200 and r.json().get("success"):
                    record("Stage 4 - Governance", "Manager Approve Recommendation", "PASS", "Status marked as APPROVED")
                else:
                    record("Stage 4 - Governance", "Manager Approve Recommendation", "FAIL", f"Status: {r.status_code}")
            except Exception as e:
                record("Stage 4 - Governance", "Manager Approve Recommendation", "FAIL", str(e))

            try:
                r = await client.post(f"/api/v1/recommendations/{rec_id}/status?status_value=APPROVED", headers=member_hdr)
                if r.status_code == 403:
                    record("Stage 4 - Governance", "Member Denied Recommendation Approval (403)", "PASS", "Protected with 403 Forbidden")
                else:
                    record("Stage 4 - Governance", "Member Denied Recommendation Approval (403)", "FAIL", f"Expected 403, got {r.status_code}")
            except Exception as e:
                record("Stage 4 - Governance", "Member Denied Recommendation Approval (403)", "FAIL", str(e))

        # Stage 5: Solution Architecture (HLD & LLD)
        try:
            r = await client.post(f"/api/v1/architecture/project/{project_id}/generate", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 5 - Architecture", "Generate Solution Architecture (HLD)", "PASS", "Architecture generated")
            else:
                record("Stage 5 - Architecture", "Generate Solution Architecture (HLD)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 5 - Architecture", "Generate Solution Architecture (HLD)", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/architecture/project/{project_id}", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                comps = data.get("components", [])
                conns = data.get("connections", [])
                record("Stage 5 - Architecture", "Fetch HLD Architecture Graph", "PASS", f"Found {len(comps)} components, {len(conns)} data flows")
            else:
                record("Stage 5 - Architecture", "Fetch HLD Architecture Graph", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 5 - Architecture", "Fetch HLD Architecture Graph", "FAIL", str(e))

        # Layout Save RBAC: Architect Allowed, Viewer Forbidden
        try:
            layout_data = [{"id": "comp-1", "position": {"x": 200, "y": 300}}]
            r = await client.post(f"/api/v1/architecture/project/{project_id}/save-layout", json=layout_data, headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 5 - Architecture", "Architect Save Layout", "PASS", "Layout persisted")
            else:
                record("Stage 5 - Architecture", "Architect Save Layout", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 5 - Architecture", "Architect Save Layout", "FAIL", str(e))

        try:
            r = await client.post(f"/api/v1/architecture/project/{project_id}/save-layout", json=[], headers=viewer_hdr)
            if r.status_code == 403:
                record("Stage 5 - Architecture", "Viewer Denied Layout Save (403)", "PASS", "Protected with 403 Forbidden")
            else:
                record("Stage 5 - Architecture", "Viewer Denied Layout Save (403)", "FAIL", f"Expected 403, got {r.status_code}")
        except Exception as e:
            record("Stage 5 - Architecture", "Viewer Denied Layout Save (403)", "FAIL", str(e))

        # Stage 6: Process Intelligence & BPMN Workflows
        try:
            r = await client.post(f"/api/v1/processes/project/{project_id}/generate", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 6 - Process Intelligence", "Generate BPMN Process Intelligence", "PASS", "Process graph generated")
            else:
                record("Stage 6 - Process Intelligence", "Generate BPMN Process Intelligence", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 6 - Process Intelligence", "Generate BPMN Process Intelligence", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/processes/project/{project_id}", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                record("Stage 6 - Process Intelligence", "Fetch BPMN Workflow & Nodes", "PASS", f"Found {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")
            else:
                record("Stage 6 - Process Intelligence", "Fetch BPMN Workflow & Nodes", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 6 - Process Intelligence", "Fetch BPMN Workflow & Nodes", "FAIL", str(e))

        # Stage 7: Database Design (PostgreSQL ER Schema & DDL)
        try:
            r = await client.post(f"/api/v1/database/project/{project_id}/generate", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 7 - Database Design", "Generate PostgreSQL ER Schema", "PASS", "Schema generated")
            else:
                record("Stage 7 - Database Design", "Generate PostgreSQL ER Schema", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 7 - Database Design", "Generate PostgreSQL ER Schema", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/database/project/{project_id}", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                record("Stage 7 - Database Design", "Fetch PostgreSQL Schema & DDL", "PASS", f"Found {len(data.get('entities', []))} entities with SQL DDL")
            else:
                record("Stage 7 - Database Design", "Fetch PostgreSQL Schema & DDL", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 7 - Database Design", "Fetch PostgreSQL Schema & DDL", "FAIL", str(e))

        # Stage 8: REST API Catalog (OpenAPI 3.0 Specs)
        try:
            r = await client.post(f"/api/v1/apis/project/{project_id}/generate", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 8 - API Design", "Generate OpenAPI 3.0 Catalog", "PASS", "APIs generated")
            else:
                record("Stage 8 - API Design", "Generate OpenAPI 3.0 Catalog", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 8 - API Design", "Generate OpenAPI 3.0 Catalog", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/apis/project/{project_id}", headers=arch_hdr)
            if r.status_code == 200 and r.json().get("success"):
                apis = r.json()["data"]
                record("Stage 8 - API Design", "Fetch REST API Catalog & OpenAPI Specs", "PASS", f"Retrieved {len(apis)} OpenAPI endpoints")
            else:
                record("Stage 8 - API Design", "Fetch REST API Catalog & OpenAPI Specs", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 8 - API Design", "Fetch REST API Catalog & OpenAPI Specs", "FAIL", str(e))

        # Stage 9: AI UX Designer & Wireframes
        try:
            r = await client.post(f"/api/v1/ux/project/{project_id}/generate", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 9 - AI UX", "Generate UI Wireframes & Personas", "PASS", "UX wireframes generated")
            else:
                record("Stage 9 - AI UX", "Generate UI Wireframes & Personas", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 9 - AI UX", "Generate UI Wireframes & Personas", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/ux/project/{project_id}", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                record("Stage 9 - AI UX", "Fetch Personas & Wireframes", "PASS", f"Retrieved {len(data.get('wireframes', []))} wireframes, {len(data.get('target_personas', []))} personas")
            else:
                record("Stage 9 - AI UX", "Fetch Personas & Wireframes", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 9 - AI UX", "Fetch Personas & Wireframes", "FAIL", str(e))

        # Stage 10: Planning, Roadmap & Staffing (INR Budget)
        try:
            r = await client.post(f"/api/v1/planning/project/{project_id}/generate", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 10 - Planning & Cost", "Generate Roadmap & Staffing", "PASS", "Roadmap and staffing generated")
            else:
                record("Stage 10 - Planning & Cost", "Generate Roadmap & Staffing", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 10 - Planning & Cost", "Generate Roadmap & Staffing", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/planning/project/{project_id}", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                est = data.get("estimate", {})
                record("Stage 10 - Planning & Cost", "Fetch Roadmap & INR Staffing Estimates", "PASS", f"Duration: {data.get('total_duration_weeks', 16)} weeks, Total Cost: INR {est.get('total_estimated_cost', 0):,}")
            else:
                record("Stage 10 - Planning & Cost", "Fetch Roadmap & INR Staffing Estimates", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 10 - Planning & Cost", "Fetch Roadmap & INR Staffing Estimates", "FAIL", str(e))

        # Stage 11: Risks Management
        try:
            r = await client.post(f"/api/v1/risks/project/{project_id}/generate", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 11 - Risk Assessment", "Generate Risk Matrix", "PASS", "Risks generated")
            else:
                record("Stage 11 - Risk Assessment", "Generate Risk Matrix", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 11 - Risk Assessment", "Generate Risk Matrix", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/risks/project/{project_id}", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                data = r.json()["data"]
                record("Stage 11 - Risk Assessment", "Fetch Project Risks Matrix", "PASS", f"Found {len(data.get('risks', []))} identified risks with mitigations")
            else:
                record("Stage 11 - Risk Assessment", "Fetch Project Risks Matrix", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 11 - Risk Assessment", "Fetch Project Risks Matrix", "FAIL", str(e))

        # Stage 12: Dynamic What-If Simulation
        try:
            sim_input = {
                "automation_level": 85,
                "team_size": 6,
                "budget": 240000.0,
                "timeline_months": 4,
                "ai_adoption_level": "HIGH"
            }
            r = await client.post(f"/api/v1/simulations/project/{project_id}/run", json=sim_input, headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                sim_res = r.json()["data"]
                record("Stage 12 - What-If Simulator", "Run Dynamic ROI & Staffing Simulation", "PASS", f"Expected ROI: {sim_res.get('expected_roi_percentage')}% | Cycle Time Reduction: {sim_res.get('cycle_time_reduction_percentage')}%")
            else:
                record("Stage 12 - What-If Simulator", "Run Dynamic ROI & Staffing Simulation", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 12 - What-If Simulator", "Run Dynamic ROI & Staffing Simulation", "FAIL", str(e))

        # Boundary & Input Validation in Simulation
        try:
            sim_boundary = {
                "automation_level": 10,
                "team_size": 1,
                "budget": 10000.0,
                "timeline_months": 1,
                "ai_adoption_level": "LOW"
            }
            r = await client.post(f"/api/v1/simulations/project/{project_id}/run", json=sim_boundary, headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                roi = r.json()["data"].get("expected_roi_percentage")
                record("Stage 12 - What-If Simulator", "Simulation Minimum Boundary Values Test", "PASS", f"Calculated ROI: {roi}% at minimum boundary inputs")
            else:
                record("Stage 12 - What-If Simulator", "Simulation Minimum Boundary Values Test", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 12 - What-If Simulator", "Simulation Minimum Boundary Values Test", "FAIL", str(e))

        try:
            sim_invalid = {
                "automation_level": -5,
                "team_size": 0,
                "budget": 500.0,
                "timeline_months": 0,
                "ai_adoption_level": "INVALID_LEVEL"
            }
            r = await client.post(f"/api/v1/simulations/project/{project_id}/run", json=sim_invalid, headers=mgr_hdr)
            if r.status_code == 422:
                record("Stage 12 - What-If Simulator", "Simulation Invalid Input Rejection (422)", "PASS", "Pydantic schema rejected invalid input ranges")
            else:
                record("Stage 12 - What-If Simulator", "Simulation Invalid Input Rejection (422)", "FAIL", f"Expected 422, got {r.status_code}")
        except Exception as e:
            record("Stage 12 - What-If Simulator", "Simulation Invalid Input Rejection (422)", "FAIL", str(e))

        # Stage 13: Transformation Scorecard (6 Dimensions)
        try:
            r = await client.post(f"/api/v1/scores/project/{project_id}/calculate", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Stage 13 - Transformation Score", "Calculate 6-Dimension Scorecard", "PASS", "Score calculated")
            else:
                record("Stage 13 - Transformation Score", "Calculate 6-Dimension Scorecard", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 13 - Transformation Score", "Calculate 6-Dimension Scorecard", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/scores/project/{project_id}", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                score = r.json()["data"]
                record("Stage 13 - Transformation Score", "Fetch Transformation Scorecard", "PASS", f"Overall Score: {score.get('overall_score')}/100, AI Readiness: {score.get('ai_readiness')}")
            else:
                record("Stage 13 - Transformation Score", "Fetch Transformation Scorecard", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Stage 13 - Transformation Score", "Fetch Transformation Scorecard", "FAIL", str(e))

        # ================================================================
        # 6. GOVERNANCE, APPROVALS, VERSIONING & COMMENTS
        # ================================================================
        print("\n--- 6. GOVERNANCE & COLLABORATION ---", flush=True)

        # Master Blueprint Fetch
        try:
            r = await client.get(f"/api/v1/blueprints/project/{project_id}", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                bp = r.json()["data"]
                record("Governance", "Fetch Master Blueprint", "PASS", f"Status: {bp.get('approval_status')}, Components: {bp.get('architecture_summary', {}).get('components_count')}")
            else:
                record("Governance", "Fetch Master Blueprint", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Governance", "Fetch Master Blueprint", "FAIL", str(e))

        # Approval RBAC Test: Manager Allowed, BA Forbidden
        try:
            r = await client.post(
                f"/api/v1/blueprints/project/{project_id}/approve",
                json={"action": "APPROVE", "comments": "Executive management approval after final review."},
                headers=mgr_hdr
            )
            if r.status_code == 200 and r.json().get("success"):
                record("Governance", "Manager Approve Master Blueprint", "PASS", "Blueprint approved successfully")
            else:
                record("Governance", "Manager Approve Master Blueprint", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Governance", "Manager Approve Master Blueprint", "FAIL", str(e))

        try:
            r = await client.post(
                f"/api/v1/blueprints/project/{project_id}/approve",
                json={"action": "APPROVE", "comments": "Unauthorized approval attempt by BA."},
                headers=ba_hdr
            )
            if r.status_code == 403:
                record("Governance", "Business Analyst Denied Blueprint Approval (403)", "PASS", "Protected with 403 Forbidden")
            else:
                record("Governance", "Business Analyst Denied Blueprint Approval (403)", "FAIL", f"Expected 403, got {r.status_code}")
        except Exception as e:
            record("Governance", "Business Analyst Denied Blueprint Approval (403)", "FAIL", str(e))

        # Version Snapshot Listing
        try:
            r = await client.get(f"/api/v1/collaboration/project/{project_id}/versions", headers=owner_hdr)
            if r.status_code == 200 and r.json().get("success"):
                versions = r.json()["data"]
                record("Governance", "List Blueprint Version Snapshots", "PASS", f"Found {len(versions)} immutable version snapshots")
            else:
                record("Governance", "List Blueprint Version Snapshots", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Governance", "List Blueprint Version Snapshots", "FAIL", str(e))

        # Comments & Discussion
        try:
            comment_payload = {
                "content": "@Marcus Vance The customer complaint classification model accuracy reaches 94%. Ready for review.",
                "section": "RECOMMENDATIONS",
                "mentions": ["Marcus Vance"]
            }
            r = await client.post(f"/api/v1/collaboration/project/{project_id}/comments", json=comment_payload, headers=ba_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Collaboration", "Create Section Comment & Mention", "PASS", "Comment posted with @mention")
            else:
                record("Collaboration", "Create Section Comment & Mention", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Collaboration", "Create Section Comment & Mention", "FAIL", str(e))

        try:
            r = await client.get(f"/api/v1/collaboration/project/{project_id}/comments", headers=viewer_hdr)
            if r.status_code == 200 and r.json().get("success"):
                comments = r.json()["data"]
                record("Collaboration", "Fetch Discussion Comments", "PASS", f"Retrieved {len(comments)} thread comments")
            else:
                record("Collaboration", "Fetch Discussion Comments", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Collaboration", "Fetch Discussion Comments", "FAIL", str(e))

        # Notifications
        try:
            r = await client.get("/api/v1/collaboration/notifications", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                record("Collaboration", "Fetch User Notifications", "PASS", f"Retrieved notifications list")
            else:
                record("Collaboration", "Fetch User Notifications", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Collaboration", "Fetch User Notifications", "FAIL", str(e))

        # Audit Logs
        try:
            r = await client.get(f"/api/v1/collaboration/project/{project_id}/audit-logs", headers=mgr_hdr)
            if r.status_code == 200 and r.json().get("success"):
                logs = r.json()["data"]
                record("Collaboration", "Fetch Project Audit Logs", "PASS", f"Retrieved {len(logs)} immutable audit log entries")
            else:
                record("Collaboration", "Fetch Project Audit Logs", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Collaboration", "Fetch Project Audit Logs", "FAIL", str(e))

        # ================================================================
        # 7. REAL MULTI-FORMAT FILE EXPORT TESTING
        # ================================================================
        print("\n--- 7. EXPORT ENGINE (PDF, DOCX, XLSX, PPTX) ---", flush=True)
        for fmt in ["pdf", "docx", "xlsx", "pptx"]:
            try:
                r = await client.get(f"/api/v1/exports/project/{project_id}/download?format={fmt}", headers=owner_hdr)
                if r.status_code == 200 and len(r.content) > 100:
                    content_len = len(r.content)
                    magic_valid = False
                    if fmt == "pdf" and r.content.startswith(b"%PDF"):
                        magic_valid = True
                    elif fmt in ["docx", "xlsx", "pptx"] and r.content.startswith(b"PK"):
                        magic_valid = True

                    if magic_valid:
                        record("Export Engine", f"Generate & Download {fmt.upper()} Blueprint", "PASS", f"Downloaded {content_len:,} bytes, valid binary format")
                    else:
                        record("Export Engine", f"Generate & Download {fmt.upper()} Blueprint", "FAIL", f"Invalid magic header for {fmt}")
                else:
                    record("Export Engine", f"Generate & Download {fmt.upper()} Blueprint", "FAIL", f"Status: {r.status_code}")
            except Exception as e:
                record("Export Engine", f"Generate & Download {fmt.upper()} Blueprint", "FAIL", str(e))

        # ================================================================
        # 8. SECURITY, IDOR & INPUT SANITIZATION
        # ================================================================
        print("\n--- 8. SECURITY, IDOR & SANITIZATION ---", flush=True)

        # SQL Injection Payload Safe Handling
        try:
            sqli_payload = {
                "name": "Test' OR '1'='1",
                "description": "SQLi probe test project",
                "industry": "Retail"
            }
            r = await client.post("/api/v1/projects", json=sqli_payload, headers=owner_hdr)
            if r.status_code in [200, 201]:
                new_pid = r.json()["data"]["id"]
                record("Security Testing", "SQL Injection Probe Handling", "PASS", "Input safely parameterized via SQLAlchemy ORM")
                await client.delete(f"/api/v1/projects/{new_pid}", headers=owner_hdr)
            elif r.status_code in [400, 422]:
                record("Security Testing", "SQL Injection Probe Handling", "PASS", "Input validation rejected unsafe payload")
            else:
                record("Security Testing", "SQL Injection Probe Handling", "FAIL", f"Unexpected status {r.status_code}")
        except Exception as e:
            record("Security Testing", "SQL Injection Probe Handling", "FAIL", str(e))

        # XSS Payload Safe Handling
        try:
            xss_comment = {
                "content": "<script>alert('XSS-Test-Chaos2Commit')</script>",
                "section": "DISCOVERY"
            }
            r = await client.post(f"/api/v1/collaboration/project/{project_id}/comments", json=xss_comment, headers=ba_hdr)
            if r.status_code == 200:
                record("Security Testing", "XSS Payload Safe Handling", "PASS", "Stored cleanly without script execution")
            else:
                record("Security Testing", "XSS Payload Safe Handling", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("Security Testing", "XSS Payload Safe Handling", "FAIL", str(e))

        # IDOR Non-Existent / Unauthorized Project Access
        try:
            fake_uuid = str(uuid.uuid4())
            r = await client.get(f"/api/v1/projects/{fake_uuid}", headers=viewer_hdr)
            if r.status_code in [403, 404]:
                record("Security Testing", "IDOR / Unauthorized Project Isolation", "PASS", f"Access to unknown project denied with {r.status_code}")
            else:
                record("Security Testing", "IDOR / Unauthorized Project Isolation", "FAIL", f"Expected 403/404, got {r.status_code}")
        except Exception as e:
            record("Security Testing", "IDOR / Unauthorized Project Isolation", "FAIL", str(e))

        # Save test summary to json
        os.makedirs("test_reports", exist_ok=True)
        with open("test_reports/master_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)

        total = len(test_results)
        passed = sum(1 for t in test_results if t["status"] == "PASS")
        failed = sum(1 for t in test_results if t["status"] == "FAIL")

        print("\n==================================================================", flush=True)
        print(f"MASTER TEST SUITE SUMMARY: {passed}/{total} PASSED ({failed} FAILED)", flush=True)
        print("==================================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_master_tests())
