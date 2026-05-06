"""Log ingestion endpoints."""

import uuid
from datetime import datetime
from fastapi import APIRouter, Request

from backend.models.incident import LogIngestRequest
from backend.utils.time import to_iso, utc_now

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.post("/ingest")
async def ingest_log(payload: LogIngestRequest, request: Request) -> dict:
    event = payload.dict()
    event_id = str(uuid.uuid4())
    event["event_id"] = event_id
    if not event.get("received_at"):
        event["received_at"] = to_iso(utc_now())
    elif isinstance(event.get("received_at"), datetime):
        event["received_at"] = to_iso(event["received_at"])
    await request.app.state.queue.enqueue(event)
    return {"status": "queued", "event_id": event_id}
