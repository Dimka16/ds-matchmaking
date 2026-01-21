from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List

_EVENTS: Deque[Dict[str, Any]] = deque(maxlen=200)


def add_event(kind: str, data: Dict[str, Any]) -> None:
    _EVENTS.appendleft({
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "data": data,
    })


def list_events(limit: int = 50) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit or 50), 200))
    return list(_EVENTS)[:limit]


def clear_events() -> None:
    _EVENTS.clear()
