"""Incident management endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from backend.utils.time import parse_iso, utc_now

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("")
async def list_incidents(
    request: Request,
    severity: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> list:
    from_dt = parse_iso(from_date)
    to_dt = parse_iso(to_date)
    return await request.app.state.store.list_incidents(
        severity=severity, from_dt=from_dt, to_dt=to_dt, limit=limit, offset=offset
    )


@router.get("/{incident_id}")
async def get_incident(request: Request, incident_id: str) -> dict:
    incident = await request.app.state.store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.get("/{incident_id}/playbook")
async def get_playbook(request: Request, incident_id: str) -> Response:
    incident = await request.app.state.store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return Response(content=incident.get("playbook_markdown", ""), media_type="text/markdown")


@router.post("/{incident_id}/approve")
async def approve_playbook(request: Request, incident_id: str) -> dict:
    incident = await request.app.state.store.update_incident(
        incident_id, {"approved": True, "updated_at": utc_now()}
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    await request.app.state.ws_manager.broadcast_json({"type": "incident_update", "data": incident})
    return {"id": incident_id, "approved": True}
