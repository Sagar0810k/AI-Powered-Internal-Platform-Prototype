from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["admin", "viewer"]


class UserCreateStrict(BaseModel):
    """Strict register payload: no extra fields allowed, validated ranges."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Strict login payload: no extra fields allowed."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    email: str
    role: str


class AgentRunRequest(BaseModel):
    """Strict payload for POST /agent/run (added in Step 3, defined early for reuse)."""

    model_config = ConfigDict(extra="forbid")

    agent_name: str = Field(min_length=1, max_length=100)
    instruction: str = Field(min_length=1, max_length=500)


class ApprovalDecision(BaseModel):
    """Strict payload for approve/reject decisions."""

    model_config = ConfigDict(extra="forbid")

    decided_by: str = Field(min_length=1, max_length=100)
