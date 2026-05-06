"""Query historical events from Postgres."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

try:
    import psycopg
except Exception:  # pragma: no cover - optional dependency
    psycopg = None


class HistoryQueryTool:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def query_recent(self, days: int = 7) -> List[Dict[str, Any]]:
        if not self.database_url or psycopg is None:
            return []
        from_dt = datetime.now(timezone.utc) - timedelta(days=days)
        query = "SELECT data FROM incidents WHERE created_at >= %s ORDER BY created_at DESC"
        try:
            with psycopg.connect(self.database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (from_dt,))
                    rows = cur.fetchall()
            return [json.loads(row[0]) for row in rows]
        except Exception:
            return []
