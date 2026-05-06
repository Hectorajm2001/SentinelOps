"""Incident data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LogIngestRequest(BaseModel):
    raw: str = Field(..., min_length=1)
    source: str = "syslog"
    received_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentSummary(BaseModel):
    id: str
    created_at: datetime
    severity: str
    attack_type: str
    source_ip: Optional[str] = None
    user: Optional[str] = None
    risk_score: int = 0
    pipeline_status: str = "COMPLETE"


class IncidentDetail(IncidentSummary):
    updated_at: datetime
    raw_log: str
    classification: Dict[str, Any] = Field(default_factory=dict)
    threat_intel: Dict[str, Any] = Field(default_factory=dict)
    correlation: Dict[str, Any] = Field(default_factory=dict)
    playbook_markdown: str = ""
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    approved: bool = False


class StatsResponse(BaseModel):
    total_today: int
    by_severity: Dict[str, int]
    avg_pipeline_seconds: float


class ApproveResponse(BaseModel):
    id: str
    approved: bool
