"""Wire schemas for the chat and health endpoints."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.decision import Decision


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    decision: Decision | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    providers: dict[str, bool] = Field(default_factory=dict)
    database: bool = False
