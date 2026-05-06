"""Incident storage with Postgres support and in-memory fallback."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    import psycopg
except Exception:  # pragma: no cover - optional dependency
    psycopg = None


class IncidentStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._use_db = bool(database_url) and psycopg is not None
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        if self._use_db:
            try:
                self._ensure_schema_sync()
            except Exception:
                self._use_db = False

    def _ensure_schema_sync(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            severity TEXT NOT NULL,
            data JSONB NOT NULL
        );
        """
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(schema)
            conn.commit()

    async def add_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        if self._use_db:
            await asyncio.to_thread(self._insert_db, incident)
            return incident
        async with self._lock:
            self._incidents[incident["id"]] = incident
        return incident

    def _insert_db(self, incident: Dict[str, Any]) -> None:
        query = "INSERT INTO incidents (id, created_at, severity, data) VALUES (%s, %s, %s, %s)"
        payload = self._serialize(incident)
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (incident["id"], incident["created_at"], incident["severity"], payload))
            conn.commit()

    async def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self._use_db:
            return await asyncio.to_thread(self._update_db, incident_id, updates)
        async with self._lock:
            incident = self._incidents.get(incident_id)
            if not incident:
                return None
            incident.update(updates)
            self._incidents[incident_id] = incident
            return incident

    def _update_db(self, incident_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        incident = self._get_db(incident_id)
        if not incident:
            return None
        incident.update(updates)
        query = "UPDATE incidents SET severity = %s, data = %s WHERE id = %s"
        payload = self._serialize(incident)
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (incident["severity"], payload, incident_id))
            conn.commit()
        return incident

    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        if self._use_db:
            return await asyncio.to_thread(self._get_db, incident_id)
        async with self._lock:
            return self._incidents.get(incident_id)

    def _get_db(self, incident_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT data FROM incidents WHERE id = %s"
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (incident_id,))
                row = cur.fetchone()
        if not row:
            return None
        payload = row[0]
        if isinstance(payload, str):
            return json.loads(payload)
        return payload

    async def list_incidents(
        self,
        severity: Optional[str] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        if self._use_db:
            return await asyncio.to_thread(self._list_db, severity, from_dt, to_dt, limit, offset)
        async with self._lock:
            incidents = list(self._incidents.values())
        if severity:
            incidents = [item for item in incidents if item.get("severity") == severity]
        if from_dt:
            incidents = [item for item in incidents if self._to_datetime(item.get("created_at")) >= from_dt]
        if to_dt:
            incidents = [item for item in incidents if self._to_datetime(item.get("created_at")) <= to_dt]
        incidents.sort(key=lambda item: self._to_datetime(item.get("created_at")), reverse=True)
        return incidents[offset : offset + limit]

    def _list_db(
        self,
        severity: Optional[str],
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        query = "SELECT data FROM incidents WHERE 1=1"
        params: List[Any] = []
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        if from_dt:
            query += " AND created_at >= %s"
            params.append(from_dt)
        if to_dt:
            query += " AND created_at <= %s"
            params.append(to_dt)
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        with psycopg.connect(self._database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        incidents: List[Dict[str, Any]] = []
        for row in rows:
            payload = row[0]
            if isinstance(payload, str):
                incidents.append(json.loads(payload))
            else:
                incidents.append(payload)
        return incidents

    async def recent_incidents(self, days: int = 7) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        from_dt = now - timedelta(days=days)
        return await self.list_incidents(from_dt=from_dt)

    async def stats(self) -> Dict[str, Any]:
        today = datetime.now(timezone.utc).date()
        incidents = await self.list_incidents(limit=1000)
        today_items = [
            item
            for item in incidents
            if self._to_datetime(item.get("created_at")).date() == today
        ]
        by_severity: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for item in today_items:
            sev = item.get("severity", "LOW")
            by_severity[sev] = by_severity.get(sev, 0) + 1
        durations = [item.get("pipeline_seconds", 0.0) for item in today_items if item.get("pipeline_seconds")]
        avg = sum(durations) / len(durations) if durations else 0.0
        return {
            "total_today": len(today_items),
            "by_severity": by_severity,
            "avg_pipeline_seconds": avg,
        }

    def _serialize(self, incident: Dict[str, Any]) -> str:
        def converter(value: Any) -> Any:
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return json.dumps(incident, default=converter)

    def _to_datetime(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return datetime.now(timezone.utc)
        return datetime.now(timezone.utc)
