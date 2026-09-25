import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.deps import get_current_user, verify_project_access, security_scheme
from app.auth.security import decode_access_token
from app.models.user import User
from app.models.project import Project
from app.models.transformation import Gap, Solution, Requirement
from app.models.planning import TransformationScore, Estimate
from app.models.collaboration import ExportJob
from app.schemas.project import ApiResponse
import io
import zipfile
from app.exports.generator import (
    generate_pdf_blueprint,
    generate_docx_blueprint,
    generate_xlsx_blueprint,
    generate_pptx_blueprint
)

router = APIRouter(prefix="/exports", tags=["Export Engine"])

@router.get("/project/{project_id}/download")
async def download_export(
    project_id: str,
    format: str = Query("pdf", pattern="^(pdf|docx|xlsx|pptx)$"),
    token: Optional[str] = Query(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
):
    jwt_token = token or (credentials.credentials if credentials else None)
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authentication token required to download blueprint.")
        
    payload = decode_access_token(jwt_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
        
    user_id = payload.get("sub")
    user_res = await db.execute(select(User).filter(User.id == user_id))
    current_user = user_res.scalars().first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User account not found.")

    project = await verify_project_access(project_id, current_user, db)
    
    # Gather project data for exporter
    gaps_res = await db.execute(select(Gap).filter(Gap.project_id == project.id))
    gaps = gaps_res.scalars().all()
    
    sol_res = await db.execute(select(Solution).filter(Solution.project_id == project.id))
    sol = sol_res.scalars().first()
    
    export_dir = "./exports_generated"
    os.makedirs(export_dir, exist_ok=True)
    
    export_data = {
        "name": project.name,
        "industry": project.industry,
        "executive_summary": sol.executive_summary if sol else (project.business_problem or "Digital transformation blueprint."),
        "gaps": [{
            "category": g.category,
            "current_state": g.current_state,
            "desired_state": g.desired_state,
            "severity": g.severity,
            "recommended_action": g.recommended_action
        } for g in gaps]
    }
    
    clean_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    base_filename = f"{clean_name}_Blueprint_{str(uuid.uuid4())[:6]}"
    
    if format == "pdf":
        file_path = os.path.join(export_dir, f"{base_filename}.pdf")
        generate_pdf_blueprint(export_data, file_path)
        media_type = "application/pdf"
        filename = f"{base_filename}.pdf"
    elif format == "docx":
        file_path = os.path.join(export_dir, f"{base_filename}.docx")
        generate_docx_blueprint(export_data, file_path)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{base_filename}.docx"
    elif format == "xlsx":
        file_path = os.path.join(export_dir, f"{base_filename}.xlsx")
        generate_xlsx_blueprint(export_data, file_path)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{base_filename}.xlsx"
    elif format == "pptx":
        file_path = os.path.join(export_dir, f"{base_filename}.pptx")
        generate_pptx_blueprint(export_data, file_path)
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        filename = f"{base_filename}.pptx"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
        
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

from pydantic import BaseModel
class ExportGenerateRequest(BaseModel):
    project_id: str
    export_format: str = "pdf"
    artifact_type: Optional[str] = "FINAL_BLUEPRINT"

@router.post("/generate", response_model=ApiResponse)
async def generate_export_job(
    req: ExportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(req.project_id, current_user, db)
    
    # Gather project data for exporter
    gaps_res = await db.execute(select(Gap).filter(Gap.project_id == project.id))
    gaps = gaps_res.scalars().all()
    
    sol_res = await db.execute(select(Solution).filter(Solution.project_id == project.id))
    sol = sol_res.scalars().first()
    
    export_dir = "./exports_generated"
    os.makedirs(export_dir, exist_ok=True)
    
    export_data = {
        "name": project.name,
        "industry": project.industry,
        "executive_summary": sol.executive_summary if sol else (project.business_problem or "Digital transformation blueprint."),
        "gaps": [{
            "category": g.category,
            "current_state": g.current_state,
            "desired_state": g.desired_state,
            "severity": g.severity,
            "recommended_action": g.recommended_action
        } for g in gaps]
    }
    
    fmt = req.export_format.lower()
    clean_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    base_filename = f"{clean_name}_Blueprint_{str(uuid.uuid4())[:6]}"
    
    if fmt == "pdf":
        file_path = os.path.join(export_dir, f"{base_filename}.pdf")
        generate_pdf_blueprint(export_data, file_path)
        filename = f"{base_filename}.pdf"
    elif fmt == "docx":
        file_path = os.path.join(export_dir, f"{base_filename}.docx")
        generate_docx_blueprint(export_data, file_path)
        filename = f"{base_filename}.docx"
    elif fmt == "xlsx":
        file_path = os.path.join(export_dir, f"{base_filename}.xlsx")
        generate_xlsx_blueprint(export_data, file_path)
        filename = f"{base_filename}.xlsx"
    elif fmt == "pptx":
        file_path = os.path.join(export_dir, f"{base_filename}.pptx")
        generate_pptx_blueprint(export_data, file_path)
        filename = f"{base_filename}.pptx"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Must be pdf, docx, xlsx, or pptx.")

    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

    export_job = ExportJob(
        id=str(uuid.uuid4()),
        project_id=project.id,
        export_type=fmt.upper(),
        file_path=file_path,
        file_name=filename,
        file_size=file_size
    )
    db.add(export_job)
    await db.commit()

    return ApiResponse(
        success=True,
        data={
            "id": export_job.id,
            "file_name": filename,
            "file_path": file_path,
            "file_size": file_size,
            "download_url": f"/api/v1/exports/project/{req.project_id}/download?format={fmt}",
            "status": "COMPLETED"
        },
        message=f"{fmt.upper()} export generated successfully"
    )

@router.get("/project/{project_id}/download-bundle")
async def download_deployment_bundle(
    project_id: str,
    token: Optional[str] = Query(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Generates a complete, ready-to-deploy Production DevOps bundle (.zip) including Dockerfile, docker-compose, render.yaml, vercel.json, and k8s specs."""
    jwt_token = token or (credentials.credentials if credentials else None)
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authentication token required.")
        
    payload = decode_access_token(jwt_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid access token.")
        
    user_id = payload.get("sub")
    user_res = await db.execute(select(User).filter(User.id == user_id))
    current_user = user_res.scalars().first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found.")

    project = await verify_project_access(project_id, current_user, db)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project.name).lower()

    # Generate bundle files
    dockerfile_content = f"""# Multi-stage Production Dockerfile for {project.name}
FROM python:3.10-slim AS backend-builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.10-slim
WORKDIR /app
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin
COPY backend/ ./backend
COPY --from=frontend-builder /app/dist ./frontend/dist

ENV ENVIRONMENT=production
ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    docker_compose_content = f"""version: '3.8'

services:
  {safe_name}-backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {safe_name}-backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@{safe_name}-db:5432/{safe_name}_db
      - JWT_SECRET=transformiq-prod-jwt-secret-key-replace-in-production
      - AI_PROVIDER=auto
      - GEMINI_MODEL=gemini-3.5-flash-lite
    depends_on:
      - {safe_name}-db
    restart: unless-stopped

  {safe_name}-db:
    image: postgres:15-alpine
    container_name: {safe_name}-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgrespassword
      - POSTGRES_DB={safe_name}_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  pgdata:
"""

    render_yaml_content = f"""services:
  - type: web
    name: {safe_name}-backend
    env: python
    rootDir: backend
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.11
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET
        generateValue: true
      - key: AI_PROVIDER
        value: auto
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_MODEL
        value: gemini-3.5-flash-lite
"""

    vercel_json_content = """{
  "version": 2,
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
"""

    k8s_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {safe_name}-app
  labels:
    app: {safe_name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {safe_name}
  template:
    metadata:
      labels:
        app: {safe_name}
    spec:
      containers:
      - name: app
        image: {safe_name}:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: {safe_name}-service
spec:
  type: ClusterIP
  selector:
    app: {safe_name}
  ports:
  - port: 80
    targetPort: 8000
"""

    readme_content = f"""# {project.name} — Live Production Deployment Guide

Generated by TransformIQ Enterprise Engine.

## 1. Quick Deploy to Render
1. Go to https://dashboard.render.com/blueprints
2. Connect your repository
3. Render automatically picks up `render.yaml` and deploys your backend.

## 2. Quick Deploy to Vercel
1. Run `cd frontend && npx vercel`
2. Follow prompts to deploy your high-performance frontend.

## 3. Self-Hosted Docker Compose
```bash
docker-compose up -d --build
```
Your backend will be live on http://localhost:8000 and connected to PostgreSQL.
"""

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("Dockerfile", dockerfile_content)
        zip_file.writestr("docker-compose.yml", docker_compose_content)
        zip_file.writestr("render.yaml", render_yaml_content)
        zip_file.writestr("vercel.json", vercel_json_content)
        zip_file.writestr("k8s-deployment.yaml", k8s_content)
        zip_file.writestr("README_DEPLOY.md", readme_content)

    zip_buffer.seek(0)
    export_dir = "./exports_generated"
    os.makedirs(export_dir, exist_ok=True)
    bundle_filename = f"{safe_name}_deployment_bundle.zip"
    file_path = os.path.join(export_dir, bundle_filename)
    
    with open(file_path, "wb") as f:
        f.write(zip_buffer.getvalue())

    return FileResponse(
        path=file_path,
        media_type="application/zip",
        filename=bundle_filename
    )
