import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.models.user import User
from app.models.project import Project
from app.models.architecture import WorkflowNode, WorkflowEdge
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/processes", tags=["Process Intelligence & BPMN"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_process_workflow(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.PROCESS_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    node_res = await db.execute(select(WorkflowNode).filter(WorkflowNode.project_id == project.id))
    nodes = node_res.scalars().all()
    
    edge_res = await db.execute(select(WorkflowEdge).filter(WorkflowEdge.project_id == project.id))
    edges = edge_res.scalars().all()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not nodes:
        result = await orchestrator.generate_process_workflow(context_data)
        node_id_map = {}
        for n in result.get("nodes", []):
            new_id = str(uuid.uuid4())
            node_id_map[n["id"]] = new_id
            db.add(WorkflowNode(
                id=new_id,
                project_id=project.id,
                node_key=n.get("node_key", n["id"]),
                label=n["label"],
                node_type=n.get("node_type", "task"),
                actor=n.get("actor"),
                system=n.get("system"),
                description=n.get("description"),
                input_data=n.get("input_data"),
                output_data=n.get("output_data"),
                swimlane=n.get("swimlane"),
                position_x=n.get("position_x", 100.0),
                position_y=n.get("position_y", 100.0)
            ))
            
        for e in result.get("edges", []):
            db.add(WorkflowEdge(
                id=str(uuid.uuid4()),
                project_id=project.id,
                source_node_key=e["source"],
                target_node_key=e["target"],
                label=e.get("label"),
                condition=e.get("condition")
            ))
        await db.commit()
        return ApiResponse(success=True, data=result, message="Process workflow auto-populated")
        
    synth = await orchestrator.generate_process_workflow(context_data)
    
    return ApiResponse(
        success=True,
        data={
            "process_name": synth.get("process_name") or f"Process Workflow for {project.name}",
            "process_summary": synth.get("process_summary") or f"End-to-end BPMN workflow for {project.name}.",
            "cycle_time_current": synth.get("cycle_time_current") or "48 Hours (Manual AS-IS)",
            "cycle_time_projected": synth.get("cycle_time_projected") or "12 Minutes (AI-Powered TO-BE)",
            "efficiency_gain": synth.get("efficiency_gain") or "87.5% Latency Reduction",
            "swimlanes": synth.get("swimlanes") or ["Customer / Ingress", "TransformIQ AI Core", "Enterprise Systems", "Human Review Specialist"],
            "nodes": [{
                "id": n.id,
                "node_key": n.node_key,
                "label": n.label,
                "node_type": n.node_type,
                "actor": n.actor,
                "description": n.description,
                "swimlane": n.swimlane,
                "position_x": n.position_x,
                "position_y": n.position_y
            } for n in nodes],
            "edges": [{
                "id": e.id,
                "source": e.source_node_key,
                "target": e.target_node_key,
                "label": e.label,
                "condition": e.condition
            } for e in edges]
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_process_workflow(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.PROCESS_GENERATE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_process_workflow(context_data)
    
    # Clear existing
    old_nodes = await db.execute(select(WorkflowNode).filter(WorkflowNode.project_id == project.id))
    for on in old_nodes.scalars().all():
        await db.delete(on)
        
    old_edges = await db.execute(select(WorkflowEdge).filter(WorkflowEdge.project_id == project.id))
    for oe in old_edges.scalars().all():
        await db.delete(oe)
        
    for n in result.get("nodes", []):
        new_id = str(uuid.uuid4())
        db.add(WorkflowNode(
            id=new_id,
            project_id=project.id,
            node_key=n.get("node_key", n["id"]),
            label=n["label"],
            node_type=n.get("node_type", "task"),
            actor=n.get("actor"),
            system=n.get("system"),
            description=n.get("description"),
            input_data=n.get("input_data"),
            output_data=n.get("output_data"),
            swimlane=n.get("swimlane"),
            position_x=n.get("position_x", 100.0),
            position_y=n.get("position_y", 100.0)
        ))
        
    for e in result.get("edges", []):
        db.add(WorkflowEdge(
            id=str(uuid.uuid4()),
            project_id=project.id,
            source_node_key=e["source"],
            target_node_key=e["target"],
            label=e.get("label"),
            condition=e.get("condition")
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_PROCESS_WORKFLOW",
        resource_type="PROCESS_WORKFLOW",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} ({current_user.role}) generated process workflow for {project.name}",
        request=request
    )
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="Process workflow generated successfully")

@router.post("/project/{project_id}/save-layout", response_model=ApiResponse)
async def save_process_layout(
    project_id: str,
    layout_data: List[Dict[str, Any]] = Body(...),
    project: Project = Depends(require_project_permission(Permission.PROCESS_EDIT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    node_res = await db.execute(select(WorkflowNode).filter(WorkflowNode.project_id == project.id))
    nodes = {n.id: n for n in node_res.scalars().all()}
    
    for item in layout_data:
        n_id = item.get("id")
        pos = item.get("position", {})
        if n_id in nodes and isinstance(pos, dict):
            if "x" in pos:
                nodes[n_id].position_x = float(pos["x"])
            if "y" in pos:
                nodes[n_id].position_y = float(pos["y"])
                
    await db.commit()
    return ApiResponse(success=True, data={"saved_count": len(layout_data)}, message="Process workflow layout saved successfully")

