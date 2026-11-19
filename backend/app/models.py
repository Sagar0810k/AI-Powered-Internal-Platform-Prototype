from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="viewer")  # admin | viewer
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, default="")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    tool_args = Column(JSON, nullable=False, default=dict)
    status = Column(String, nullable=False, default="PROPOSED")  # PROPOSED | APPROVED | REJECTED | EXECUTED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String, nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    detail = Column(Text, default="")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
