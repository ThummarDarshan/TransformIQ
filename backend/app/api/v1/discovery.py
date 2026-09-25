import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.config.settings import settings
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.auth.rate_limiter import rate_limit
from app.models.user import User
from app.models.project import Project, BusinessContext, Document, DocumentChunk
from app.models.collaboration import Conversation, Message
from app.models.transformation import Question
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator
from app.documents.extractor import search_relevant_chunks

router = APIRouter(prefix="/discovery", tags=["Discovery & AI Companion"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = "en"

class UpdateConversationRequest(BaseModel):
    title: str

@router.get("/project/{project_id}/questions", response_model=ApiResponse)
async def get_discovery_questions(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    q_res = await db.execute(select(Question).filter(Question.project_id == project.id).order_by(Question.created_at.asc()))
    questions = q_res.scalars().all()
    
    if not questions:
        from app.ai.smart_engine import detect_domain
        ctx_data = {
            "name": project.name,
            "industry": project.industry,
            "business_problem": project.business_problem,
            "business_objective": project.business_objective
        }
        domain = detect_domain(ctx_data)
        if domain == "HR_RECRUITING":
            default_qs = [
                {"id": "q1", "question_text": "What is the average monthly resume volume received across all recruiters?", "category": "Candidate Ingestion", "suggested_answers": ["100 - 500 resumes/mo", "500 - 2,000 resumes/mo", "2,000+ resumes/mo"]},
                {"id": "q2", "question_text": "How many recruiters require daily attendance and activity tracking?", "category": "Team Operations", "suggested_answers": ["1 - 5 Recruiters", "6 - 15 Recruiters (e.g. 12 Recruiters)", "15+ Recruiters"]},
                {"id": "q3", "question_text": "What is your target client digital onboarding turnaround time?", "category": "Client SLAs", "suggested_answers": ["Under 3 Days (Target)", "3 - 5 Days", "Under 24 Hours"]}
            ]
        elif domain == "RETAIL_SUPPLY_CHAIN":
            default_qs = [
                {"id": "q1", "question_text": "How many store POS terminals and central warehouses need real-time synchronization?", "category": "Store Architecture", "suggested_answers": ["5 - 20 Stores", "20 - 50 Stores", "50+ Retail Locations"]},
                {"id": "q2", "question_text": "What is the current estimated revenue impact from stockouts and phantom inventory?", "category": "Supply Chain Friction", "suggested_answers": ["5% - 10% lost sales", "10% - 20% lost revenue", "Critical multi-day stockouts"]},
                {"id": "q3", "question_text": "Is offline-first checkout capability required during store internet disruptions?", "category": "Reliability", "suggested_answers": ["Yes, zero store sales downtime required", "Preferred with local cache", "Not required"]}
            ]
        else:
            default_qs = [
                {"id": "q1", "question_text": "What is the primary operational friction point in this workflow?", "category": "Problem Statement", "suggested_answers": ["48h turnaround time", "High manual error rate", "Lack of real-time visibility"]},
                {"id": "q2", "question_text": "What legacy software systems are currently handling these requests?", "category": "Technology Landscape", "suggested_answers": ["Custom On-Prem SQL", "Salesforce / SAP ERP", "Shared Spreadsheets & Mailboxes"]},
                {"id": "q3", "question_text": "What is the target straight-through processing (STP) rate for phase 1?", "category": "Target Outcomes", "suggested_answers": [">75% STP", ">50% STP", ">90% STP"]}
            ]
        return ApiResponse(success=True, data=default_qs, message="Contextual discovery questions")
        
    return ApiResponse(
        success=True,
        data=[{
            "id": q.id,
            "question_text": q.question_text,
            "category": q.category,
            "answer_text": q.answer_text,
            "suggested_answers": q.suggested_answers,
            "is_answered": q.is_answered
        } for q in questions]
    )

@router.get("/project/{project_id}/conversations", response_model=ApiResponse)
async def get_project_conversations(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all saved chat conversation threads for this project."""
    conv_res = await db.execute(
        select(Conversation)
        .filter(Conversation.project_id == project.id, Conversation.module == "DISCOVERY")
        .order_by(Conversation.created_at.desc())
    )
    conversations = conv_res.scalars().all()
    
    results = []
    for c in conversations:
        msg_res = await db.execute(
            select(Message)
            .filter(Message.conversation_id == c.id)
            .order_by(Message.created_at.asc())
        )
        msgs = msg_res.scalars().all()
        last_msg = msgs[-1].content if msgs else ""
        
        results.append({
            "id": c.id,
            "title": c.title or "Discovery Chat",
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "message_count": len(msgs),
            "preview": last_msg[:80] + "..." if len(last_msg) > 80 else last_msg
        })
        
    return ApiResponse(
        success=True,
        data=results,
        message=f"Retrieved {len(results)} conversations"
    )

@router.get("/project/{project_id}/conversation/{conversation_id}", response_model=ApiResponse)
async def get_single_conversation(
    project_id: str,
    conversation_id: str,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all messages for a specific conversation session."""
    conv_res = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.project_id == project.id)
    )
    conv = conv_res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    msg_res = await db.execute(
        select(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc())
    )
    db_messages = msg_res.scalars().all()
    
    return ApiResponse(
        success=True,
        data={
            "conversation_id": conv.id,
            "title": conv.title,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "suggested_actions": m.suggested_actions or [],
                    "structured_data": m.structured_data,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                for m in db_messages
            ]
        },
        message="Conversation loaded"
    )

@router.post("/project/{project_id}/conversation", response_model=ApiResponse)
async def create_new_conversation(
    project_id: str,
    title: Optional[str] = Body(None, embed=True),
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat conversation session thread."""
    new_id = str(uuid.uuid4())
    conv = Conversation(
        id=new_id,
        project_id=project.id,
        title=title or "New Discovery Chat",
        module="DISCOVERY"
    )
    db.add(conv)
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"id": conv.id, "title": conv.title, "created_at": conv.created_at.isoformat() if conv.created_at else None},
        message="New conversation session created"
    )

@router.patch("/project/{project_id}/conversation/{conversation_id}", response_model=ApiResponse)
async def rename_conversation(
    project_id: str,
    conversation_id: str,
    payload: UpdateConversationRequest,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rename an existing conversation thread."""
    conv_res = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.project_id == project.id)
    )
    conv = conv_res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    conv.title = payload.title.strip()
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"id": conv.id, "title": conv.title},
        message="Conversation renamed successfully"
    )

@router.delete("/project/{project_id}/conversation/{conversation_id}", response_model=ApiResponse)
async def delete_conversation(
    project_id: str,
    conversation_id: str,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific conversation session thread."""
    conv_res = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.project_id == project.id)
    )
    conv = conv_res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    await db.delete(conv)
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"deleted": True, "conversation_id": conversation_id},
        message="Conversation deleted"
    )

@router.get("/project/{project_id}/chat/history", response_model=ApiResponse)
async def get_chat_history(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the active conversation and all past messages for this project."""
    conv_res = await db.execute(
        select(Conversation)
        .filter(Conversation.project_id == project.id, Conversation.module == "DISCOVERY")
        .order_by(Conversation.created_at.desc())
    )
    conv = conv_res.scalars().first()
    
    if not conv:
        return ApiResponse(
            success=True,
            data={"conversation_id": None, "title": "Discovery Session", "messages": []},
            message="No existing chat history found"
        )
    
    msg_res = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
    )
    db_messages = msg_res.scalars().all()
    
    formatted_messages = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "suggested_actions": m.suggested_actions or [],
            "structured_data": m.structured_data,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in db_messages
    ]
    
    return ApiResponse(
        success=True,
        data={
            "conversation_id": conv.id,
            "title": conv.title,
            "messages": formatted_messages
        },
        message=f"Loaded {len(formatted_messages)} chat messages"
    )

@router.delete("/project/{project_id}/chat/history", response_model=ApiResponse)
async def clear_chat_history(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear chat conversation history for this project."""
    conv_res = await db.execute(
        select(Conversation)
        .filter(Conversation.project_id == project.id, Conversation.module == "DISCOVERY")
    )
    conversations = conv_res.scalars().all()
    for c in conversations:
        await db.delete(c)
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"cleared": True},
        message="Chat history cleared successfully"
    )

@router.post("/project/{project_id}/chat", response_model=ApiResponse)
async def chat_with_ai_companion(
    project_id: str,
    req: ChatRequest,
    project: Project = Depends(require_project_permission(Permission.DISCOVERY_CHAT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("chat", settings.CHAT_RATE_LIMIT_PER_MINUTE))
):
    """
    Main Chatbot Endpoint:
    - Multi-turn conversation memory
    - RAG retrieval over project documents and website chunks
    - Resilient multi-provider routing (Gemini -> Groq -> OpenRouter -> OpenAI -> Azure)
    - Full persistence of conversations and messages
    """
    # 1. Fetch project business context
    ctx_res = await db.execute(select(BusinessContext).filter(BusinessContext.project_id == project.id))
    ctx = ctx_res.scalars().first()
    context_text = ctx.summary if ctx else (project.business_problem or "")
    
    project_context = (
        f"Project Name: {project.name}\n"
        f"Industry Vertical: {project.industry or 'Enterprise Services'}\n"
        f"Business Problem Statement: {project.business_problem or 'Operational bottlenecks and legacy manual workflows'}\n"
        f"Business Objectives: {project.business_objective or 'Streamline processes and achieve autonomous straight-through processing'}\n"
        f"Current Systems: {project.current_systems or 'Spreadsheets, Legacy SQL, Shared Mailboxes'}\n"
        f"Expected Outcome: {project.expected_outcome or 'Reduce latency from 48h to 15m, 80%+ STP'}\n"
        f"Business Context Summary: {context_text[:1200]}"
    )

    # 2. RAG Retrieval from Document Chunks
    rag_context = ""
    if settings.CHAT_RAG_ENABLED:
        try:
            chunks_res = await db.execute(
                select(DocumentChunk, Document.filename)
                .join(Document, DocumentChunk.document_id == Document.id)
                .filter(Document.project_id == project.id)
            )
            all_chunks_raw = chunks_res.all()
            chunk_dicts = [
                {
                    "content": c[0].content,
                    "filename": c[1],
                    "page_number": c[0].page_number or 1,
                    "chunk_index": c[0].chunk_index
                }
                for c in all_chunks_raw
            ]
            if chunk_dicts:
                relevant_chunks = search_relevant_chunks(chunk_dicts, req.message, top_k=settings.RAG_TOP_K)
                if relevant_chunks:
                    rag_snippets = []
                    for idx, chk in enumerate(relevant_chunks):
                        rag_snippets.append(
                            f"[Source #{idx+1}: {chk['filename']} (Page {chk['page_number']})]\n{chk['content']}"
                        )
                    rag_context = "\n\n".join(rag_snippets)
        except Exception as e:
            # Non-blocking RAG fallback
            pass

    # 3. Find or create persistent conversation thread
    conv = None
    if req.conversation_id:
        conv_res = await db.execute(
            select(Conversation).filter(Conversation.id == req.conversation_id, Conversation.project_id == project.id)
        )
        conv = conv_res.scalars().first()
    
    if not conv:
        conv_res = await db.execute(
            select(Conversation)
            .filter(Conversation.project_id == project.id, Conversation.module == "DISCOVERY")
            .order_by(Conversation.created_at.desc())
        )
        conv = conv_res.scalars().first()
        
    if not conv:
        clean_title = req.message.strip().split("\n")[0][:40]
        if len(req.message.strip()) > 40:
            clean_title += "..."
        conv = Conversation(
            id=req.conversation_id or str(uuid.uuid4()),
            project_id=project.id,
            title=clean_title or f"{project.name} Chat",
            module="DISCOVERY"
        )
        db.add(conv)
        await db.flush()
    else:
        if conv.title in ["New Discovery Chat", "AI Discovery Session", "Discovery Session", f"{project.name} Discovery Session", f"{project.name} Discovery Chat"]:
            clean_title = req.message.strip().split("\n")[0][:40]
            if len(req.message.strip()) > 40:
                clean_title += "..."
            conv.title = clean_title

    # 4. Load past messages for multi-turn conversational memory
    msg_history_res = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
    )
    past_db_messages = msg_history_res.scalars().all()
    
    # Format message history (limit to last 10 messages for token efficiency)
    messages_for_llm: List[Dict[str, str]] = []
    for m in past_db_messages[-10:]:
        messages_for_llm.append({"role": m.role, "content": m.content})
    
    # Append current user query
    messages_for_llm.append({"role": "user", "content": req.message})

    # 5. Persist User message
    user_msg_id = str(uuid.uuid4())
    user_msg = Message(
        id=user_msg_id,
        conversation_id=conv.id,
        role="user",
        content=req.message,
        suggested_actions=[]
    )
    db.add(user_msg)
    
    # 6. Execute AI Orchestrator with memory & RAG grounding
    ai_reply, provider_used = await orchestrator.chat_companion(
        messages=messages_for_llm,
        project_context=project_context,
        rag_context=rag_context,
        language=req.language or "en"
    )
    
    suggested_actions = [
        "Analyze AS-IS process flow & bottlenecks",
        "Extract functional & compliance requirements",
        "Execute 8-dimension gap matrix",
        "Calculate TransformIQ readiness score"
    ]
    
    structured_metadata = {
        "ai_provider": provider_used,
        "rag_sources_count": len(rag_context.split("[Source #")) - 1 if rag_context else 0,
        "language": req.language or "en"
    }

    # 7. Persist AI Assistant reply
    assistant_msg_id = str(uuid.uuid4())
    assistant_msg = Message(
        id=assistant_msg_id,
        conversation_id=conv.id,
        role="assistant",
        content=ai_reply,
        structured_data=structured_metadata,
        suggested_actions=suggested_actions
    )
    db.add(assistant_msg)
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={
            "id": assistant_msg_id,
            "message": ai_reply,
            "reply": ai_reply,
            "conversation_id": conv.id,
            "conversation_title": conv.title,
            "project_id": project.id,
            "ai_provider": provider_used,
            "suggested_actions": suggested_actions,
            "structured_data": structured_metadata
        },
        message="AI response generated and persisted"
    )
