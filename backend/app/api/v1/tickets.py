import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/tickets", tags=["Live Connected Tickets & App API"])

class TicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    category: Optional[str] = "Customer Support & Inquiries"
    priority: Optional[str] = "MEDIUM"
    details: Optional[str] = None
    email: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

class TicketResponse(BaseModel):
    id: str
    title: str
    category: str
    priority: str
    status: str
    details: Optional[str] = None
    date: str
    created_at: str

# In-memory synchronized store with initial realistic business records
LIVE_TICKETS: List[Dict[str, Any]] = [
    {
        "id": "ITM-101",
        "title": "Payment Gateway Webhook Timeout",
        "category": "Billing & Payment Gateway",
        "priority": "HIGH",
        "status": "AUTO_RESOLVED",
        "details": "Stripe webhook retry latency exceeded 5000ms threshold.",
        "date": "Just now",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "ITM-102",
        "title": "Carrier Tracking ID Synchronization",
        "category": "Order Fulfillment & Logistics",
        "priority": "MEDIUM",
        "status": "IN_PROGRESS",
        "details": "BlueDart tracking API returned 200 with batch tracking IDs.",
        "date": "4m ago",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "ITM-103",
        "title": "Bulk Inventory Discrepancy Reconciliation",
        "category": "Inventory Sync & Warehousing",
        "priority": "HIGH",
        "status": "QUEUED",
        "details": "SKU #9024 warehouse count differs from Shopify catalog by 14 units.",
        "date": "11m ago",
        "created_at": datetime.utcnow().isoformat()
    }
]

@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_tickets():
    """Retrieve all synchronized live application tickets."""
    return LIVE_TICKETS

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_new_ticket(payload: TicketCreate):
    """
    Ingests and automatically categorizes a new ticket from the frontend web application.
    """
    title_clean = payload.title.strip()
    if not title_clean:
        raise HTTPException(status_code=400, detail="Title cannot be blank")

    # Smart automatic status resolution
    prio = (payload.priority or "MEDIUM").upper()
    auto_status = "ESCALATED" if prio == "HIGH" else "AUTO_ROUTED"

    new_id = f"ITM-{len(LIVE_TICKETS) + 101}"
    new_record = {
        "id": new_id,
        "title": title_clean,
        "category": payload.category or "General Inquiry",
        "priority": prio,
        "status": auto_status,
        "details": payload.details or f"Automated ingestion for {title_clean}",
        "date": "Just now",
        "created_at": datetime.utcnow().isoformat()
    }

    # Prepend for real-time feed
    LIVE_TICKETS.insert(0, new_record)
    return new_record

@router.delete("/{ticket_id}", response_model=Dict[str, Any])
async def delete_ticket(ticket_id: str):
    """Deletes a ticket by ID."""
    global LIVE_TICKETS
    before_count = len(LIVE_TICKETS)
    LIVE_TICKETS = [t for t in LIVE_TICKETS if t["id"] != ticket_id]
    if len(LIVE_TICKETS) == before_count:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"deleted": True, "id": ticket_id}
