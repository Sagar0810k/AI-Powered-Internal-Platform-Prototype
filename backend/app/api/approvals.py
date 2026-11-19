import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import agent, models, schemas
from app.api.deps import get_db, require_role
from app.middleware import agent_runs_total, approvals_total

router = APIRouter(tags=["approvals"])

admin_only = require_role("admin")


def _approval_to_dict(req: models.ApprovalRequest) -> dict:
    return {
        "id": req.id,
        "agent_name": req.agent_name,
        "tool_name": req.tool_name,
        "tool_args": req.tool_args,
        "status": req.status,
        "created_at": req.created_at,
        "decided_at": req.decided_at,
        "decided_by": req.decided_by,
    }


@router.post("/approvals/agent/run")
def run_agent(payload: schemas.AgentRunRequest, db: Session = Depends(get_db)) -> list:
    """Agent proposes 1-3 tool calls -> each becomes a PROPOSED ApprovalRequest. Nothing executes yet."""
    actions = agent.propose_actions(payload.instruction)
    agent_runs_total.inc()
    proposals = []

    for action in actions:
        req = models.ApprovalRequest(
            agent_name=payload.agent_name,
            tool_name=action["tool_name"],
            tool_args=action["tool_args"],
            status="PROPOSED",
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        proposals.append(
            {
                "approval_id": req.id,
                "tool_name": req.tool_name,
                "tool_args": req.tool_args,
                "rationale": action.get("rationale", ""),
            }
        )

    return proposals


@router.get("/approvals")
def list_approvals(status_filter: Optional[str] = None, db: Session = Depends(get_db)) -> list:
    query = db.query(models.ApprovalRequest).order_by(models.ApprovalRequest.created_at.desc())
    if status_filter:
        query = query.filter(models.ApprovalRequest.status == status_filter)
    items = query.all()
    return [_approval_to_dict(i) for i in items]


@router.post("/approvals/{approval_id}/approve")
def approve(
    approval_id: int,
    decision: schemas.ApprovalDecision,
    db: Session = Depends(get_db),
    admin: models.User = Depends(admin_only),
) -> dict:
    """Admin approves a PROPOSED request -> mark APPROVED -> mocked execute -> EXECUTED + audit event."""
    req = db.get(models.ApprovalRequest, approval_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approval_not_found")
    if req.status != "PROPOSED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="approval_not_pending")

    req.status = "APPROVED"
    req.decided_at = datetime.now(timezone.utc)
    req.decided_by = decision.decided_by
    db.commit()
    db.refresh(req)

    result = agent.execute_tool(req.tool_name, req.tool_args)
    req.status = "EXECUTED"
    approvals_total.labels(status="executed").inc()
    db.add(
        models.AuditEvent(
            request_id=req.id,
            action="approve",
            actor=decision.decided_by,
            detail=json.dumps(result),
        )
    )
    db.commit()
    db.refresh(req)
    return _approval_to_dict(req)


@router.post("/approvals/{approval_id}/reject")
def reject(
    approval_id: int,
    decision: schemas.ApprovalDecision,
    db: Session = Depends(get_db),
    admin: models.User = Depends(admin_only),
) -> dict:
    """Admin rejects a PROPOSED request -> mark REJECTED + audit event."""
    req = db.get(models.ApprovalRequest, approval_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approval_not_found")
    if req.status != "PROPOSED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="approval_not_pending")

    req.status = "REJECTED"
    approvals_total.labels(status="rejected").inc()
    req.decided_at = datetime.now(timezone.utc)
    req.decided_by = decision.decided_by
    db.add(
        models.AuditEvent(
            request_id=req.id,
            action="reject",
            actor=decision.decided_by,
            detail="rejected_by_human",
        )
    )
    db.commit()
    db.refresh(req)
    return _approval_to_dict(req)


@router.get("/audit")
def list_audit(db: Session = Depends(get_db)) -> list:
    events = db.query(models.AuditEvent).order_by(models.AuditEvent.timestamp.desc()).all()
    return [
        {
            "id": e.id,
            "request_id": e.request_id,
            "action": e.action,
            "actor": e.actor,
            "detail": e.detail,
            "timestamp": e.timestamp,
        }
        for e in events
    ]
