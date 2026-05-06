"""Event queue abstraction backed by Redis or a local fallback."""

import asyncio
import json
from typing import Any, Dict, Optional

try:
    import redis.asyncio as redis_async
except Exception:  # pragma: no cover - optional dependency
    redis_async = None


class EventQueue:
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis = None
        self._local_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        if redis_async is not None:
            self._redis = redis_async.from_url(redis_url, decode_responses=True)

    async def enqueue(self, event: Dict[str, Any]) -> None:
        if self._redis is not None:
            payload = json.dumps(event)
            await self._redis.lpush("sentinelops:events", payload)
            return
        await self._local_queue.put(event)

    async def dequeue(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        if self._redis is not None:
            result = await self._redis.brpop("sentinelops:events", timeout=timeout)
            if not result:
                return None
            _, payload = result
            return json.loads(payload)
        try:
            return await asyncio.wait_for(self._local_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.close()
