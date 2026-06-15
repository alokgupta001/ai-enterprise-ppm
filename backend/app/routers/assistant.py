"""
PMO Assistant router — chat, streaming, and recommendations endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import json
import time

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.project import Conversation, AIMessage, AIRecommendation, Project
from app.services.context_builder import build_project_context
from app.agents.orchestrator import route, classify_question
from app.services.root_cause import run_root_cause_analysis
from app.services.nl_to_sql import execute_nl_query

router = APIRouter(prefix="/api/assistant", tags=["PMO Assistant"])


class ChatRequest(BaseModel):
    org_id: UUID
    conversation_id: Optional[UUID] = None
    message: str


class ConversationCreate(BaseModel):
    org_id: UUID
    title: Optional[str] = "New Discussion"


@router.post("/conversations")
def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation thread."""
    # Verify user belongs to the organization
    if current_user.organization_id != payload.org_id:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
    
    conv = Conversation(org_id=payload.org_id, title=payload.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": str(conv.id), "title": conv.title}


@router.get("/conversations")
def list_conversations(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List conversations for an organization."""
    # Verify user belongs to the organization
    try:
        org_uuid = UUID(org_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid organization ID format")
    
    if current_user.organization_id != org_uuid:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
    
    convs = db.query(Conversation).filter(
        Conversation.org_id == org_uuid,
        Conversation.is_deleted.is_(False)
    ).order_by(Conversation.created_at.desc()).all()

    return [
        {"id": str(c.id), "title": c.title, "created_at": str(c.created_at)}
        for c in convs
    ]


def process_assistant_message(org_id: str, message: str, db: Session) -> dict:
    msg_lower = message.lower()
    
    # 1. Check for root cause diagnostic requests
    diagnostic_keywords = ["why", "diagnose", "root cause", "what's wrong", "reason for", "mitigate", "mitigation", "issue", "bottleneck"]
    is_diagnostic = any(kw in msg_lower for kw in diagnostic_keywords)
    
    if is_diagnostic:
        # Find all projects for this org
        projects = db.query(Project).filter(
            Project.org_id == org_id,
            Project.is_deleted.is_(False)
        ).all()
        
        # Match project name
        matched_project = None
        for p in projects:
            if p.name.lower() in msg_lower:
                matched_project = p
                break
                
        if matched_project:
            analysis = run_root_cause_analysis(str(matched_project.id), db)
            if analysis.get("status") != "error":
                # Format the analysis into a beautiful markdown response
                issues_list = "\n".join([f"- {i}" for i in analysis.get("primary_issues", [])])
                causes_list = "\n".join([f"- {c}" for c in analysis.get("root_causes", [])])
                mitigations_list = "\n".join([f"- {m}" for m in analysis.get("mitigations", [])])
                
                response_text = (
                    f"### Root Cause Diagnosis for **{matched_project.name}**\n\n"
                    f"{analysis.get('health_summary', '')}\n\n"
                    f"#### Primary Issues Identified:\n{issues_list}\n\n"
                    f"#### Underlying Root Causes:\n{causes_list}\n\n"
                    f"#### Recommended Mitigations:\n{mitigations_list}\n\n"
                    f"*Analyzed using: {analysis.get('analyzed_by', 'Fallback Engine')}*"
                )
                return {
                    "agent": "Root Cause Diagnostic Engine",
                    "agent_key": "risk",
                    "response": response_text
                }
                
    # 2. Check for NL to SQL queries
    sql_keywords = ["how many", "list all", "which project", "what is the budget", "show me", "query", "table", "sql", "budget of", "assigned to", "who is", "velocity of", "risks of"]
    is_sql = any(kw in msg_lower for kw in sql_keywords)
    
    if is_sql:
        sql_result = execute_nl_query(message, org_id, db)
        if sql_result.get("results") or sql_result.get("error"):
            # Format results in a neat markdown table
            results = sql_result["results"]
            error = sql_result["error"]
            query = sql_result["query"]
            
            if error:
                response_text = f"**Database Query Error:** {error}\n\n*Attempted Query:*\n```sql\n{query}\n```"
            elif not results:
                response_text = f"I executed the database query, but no matching records were found.\n\n*Executed Query:*\n```sql\n{query}\n```"
            else:
                # Build markdown table
                headers = list(results[0].keys())
                header_line = "| " + " | ".join(headers) + " |"
                separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
                
                rows_lines = []
                for r in results:
                    row_vals = [str(r.get(h, "")) for h in headers]
                    rows_lines.append("| " + " | ".join(row_vals) + " |")
                    
                table_md = "\n".join([header_line, separator_line] + rows_lines)
                
                response_text = (
                    f"### Database Query Results\n\n"
                    f"Here is the requested information retrieved from the live database:\n\n"
                    f"{table_md}\n\n"
                    f"*Executed SQL query:*\n```sql\n{query}\n```"
                )
                
            return {
                "agent": "NL to SQL DB Engine",
                "agent_key": "resource" if "resource" in msg_lower or "team" in msg_lower else "timeline" if "sprint" in msg_lower or "velocity" in msg_lower else "risk",
                "response": response_text
            }
            
    # 3. Default to Multi-Agent Orchestrator
    # Build context
    context = build_project_context(org_id, db)
    result = route(message, context)
    return result


@router.post("/chat")
def chat_endpoint(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get an AI response from the orchestrator."""
    # Verify user belongs to the organization
    if current_user.organization_id != payload.org_id:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
    
    # Create conversation if not provided
    if payload.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        # Verify conversation belongs to the user's organization
        if conv.org_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="User does not have access to this conversation")
    else:
        conv = Conversation(org_id=payload.org_id, title=payload.message[:80])
        db.add(conv)
        db.flush()

    # Process message using routing engine
    result = process_assistant_message(str(payload.org_id), payload.message, db)

    # Save user message
    user_msg = AIMessage(
        conversation_id=conv.id,
        role="user",
        content=payload.message,
    )
    db.add(user_msg)

    # Save assistant message
    ai_msg = AIMessage(
        conversation_id=conv.id,
        role="assistant",
        content=result["response"],
        agent_used=result.get("agent", "orchestrator"),
    )
    db.add(ai_msg)
    db.commit()

    return {
        "conversation_id": str(conv.id),
        "agent": result.get("agent", "orchestrator"),
        "agent_key": result.get("agent_key", "risk"),
        "response": result["response"],
    }


@router.post("/chat/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream an AI response using Server-Sent Events."""
    # Verify user belongs to the organization
    if current_user.organization_id != payload.org_id:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
    
    # Process message using routing engine
    result = process_assistant_message(str(payload.org_id), payload.message, db)
    full_text = result["response"]

    # Save to DB
    if payload.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        # Verify conversation belongs to the user's organization
        if conv.org_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="User does not have access to this conversation")
    else:
        conv = Conversation(org_id=payload.org_id, title=payload.message[:80])
        db.add(conv)
        db.flush()

    db.add(AIMessage(conversation_id=conv.id, role="user", content=payload.message))
    db.add(AIMessage(
        conversation_id=conv.id, role="assistant",
        content=full_text, agent_used=result.get("agent")
    ))
    db.commit()

    async def event_generator():
        """Simulate token-by-token streaming for SSE."""
        # Send metadata
        yield f"data: {json.dumps({'type': 'meta', 'agent': result.get('agent', 'orchestrator')})}\n\n"

        # Stream response in chunks
        words = full_text.split(" ")
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            yield f"data: {json.dumps({'type': 'token', 'content': chunk + ' '})}\n\n"
            # Small delay to simulate streaming
            import asyncio
            await asyncio.sleep(0.03)

        yield f"data: {json.dumps({'type': 'done', 'conversation_id': str(conv.id)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify user belongs to the conversation's organization
    if conv.org_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="User does not have access to this conversation")
    
    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id,
        AIMessage.is_deleted.is_(False)
    ).order_by(AIMessage.created_at).all()

    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "agent_used": m.agent_used,
            "created_at": str(m.created_at),
        }
        for m in messages
    ]


@router.get("/recommendations")
def get_recommendations(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated recommendations for an organization."""
    # Verify user belongs to the organization
    try:
        org_uuid = UUID(org_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid organization ID format")
    
    if current_user.organization_id != org_uuid:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
    
    recs = db.query(AIRecommendation).filter(
        AIRecommendation.org_id == org_uuid,
        AIRecommendation.is_deleted.is_(False)
    ).order_by(AIRecommendation.created_at.desc()).all()

    return [
        {
            "id": str(r.id),
            "type": r.type,
            "priority": r.priority,
            "title": r.title,
            "description": r.description,
            "action_items": r.action_items,
            "created_at": str(r.created_at),
        }
        for r in recs
    ]
