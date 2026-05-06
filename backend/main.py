"""FastAPI entrypoint for SentinelOps."""

import asyncio
import os
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import incidents, logs, stats, ws
from backend.services.incident_store import IncidentStore
from backend.services.pipeline import AgentsPipeline
from backend.services.queue import EventQueue
from backend.services.websocket_manager import ConnectionManager
from backend.utils.time import utc_now

app = FastAPI(title="SentinelOps API", version="0.1.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(incidents.router)
app.include_router(stats.router)
app.include_router(ws.router)


@app.get("/")
async def root() -> dict:
    return {"service": "sentinelops", "status": "running"}


async def event_consumer(app_instance: FastAPI) -> None:
    while not app_instance.state.stop_event.is_set():
        event = await app_instance.state.queue.dequeue(timeout=1.0)
        if not event:
            await asyncio.sleep(0.05)
            continue
        history = await app_instance.state.store.recent_incidents(days=7)
        incident = await app_instance.state.pipeline.run(event, history)
        await app_instance.state.store.add_incident(incident)
        await app_instance.state.ws_manager.broadcast_json(
            {"type": "incident_update", "data": incident}
        )


@app.on_event("startup")
async def startup() -> None:
    app.state.queue = EventQueue(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    app.state.store = IncidentStore(os.getenv("DATABASE_URL", ""))
    app.state.pipeline = AgentsPipeline(
        vllm_base_url=os.getenv("VLLM_BASE_URL", "http://mock-vllm:8000/v1"),
        model_name=os.getenv("VLLM_MODEL_NAME", "llama-70b"),
    )
    app.state.ws_manager = ConnectionManager()
    app.state.stop_event = asyncio.Event()
    app.state.consumer_task = asyncio.create_task(event_consumer(app))


@app.on_event("shutdown")
async def shutdown() -> None:
    app.state.stop_event.set()
    await app.state.queue.close()
    task = app.state.consumer_task
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
