"""Stats and health endpoints."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def get_stats(request: Request) -> dict:
    return await request.app.state.store.stats()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
