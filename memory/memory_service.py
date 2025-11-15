"""
Simple in-memory + file-backed memory service to simulate:
- Session service (short-term)
- Long-term memory (user history & trends)
"""

import json
from pathlib import Path
from typing import Dict, Any, List

MEMORY_DIR = Path("memory_store")
MEMORY_DIR.mkdir(exist_ok=True)

SESSION_FILE = MEMORY_DIR / "sessions.json"
LONG_TERM_FILE = MEMORY_DIR / "long_term.json"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_json(path: Path, data: Dict[str, Any]):
    path.write_text(json.dumps(data, indent=2))


class MemoryService:
    """
    Implementation:
    - session_store: chat context per session_id
    - long_term_store: list of emissions summaries per session_id
    """

    def __init__(self):
        self.session_store = _load_json(SESSION_FILE)
        self.long_term_store = _load_json(LONG_TERM_FILE)

    async def get_session_context(self, session_id: str) -> List[Dict[str, Any]]:
        return self.session_store.get(session_id, [])

    async def append_session_message(
            self, session_id: str, role: str, content: str
    ):
        history = self.session_store.setdefault(session_id, [])
        history.append({"role": role, "content": content})
        _save_json(SESSION_FILE, self.session_store)

    async def load_user_profile(self, session_id: str) -> Dict[str, Any]:
        """
        For now, user profile == last long-term summary + few hints.
        """
        history = self.long_term_store.get(session_id, [])
        if not history:
            return {}
        latest = history[-1]
        return {"last_total": latest.get("total", 0)}

    async def append_session_emissions(
            self, session_id: str, emissions: Dict[str, Any]
    ):
        hist = self.long_term_store.setdefault(session_id, [])
        hist.append(emissions)
        _save_json(LONG_TERM_FILE, self.long_term_store)

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.long_term_store.get(session_id, [])

    async def save_pending_request(self, session_id: str, text: str):
        ctx = self.session_store.setdefault(session_id, [])
        ctx.append({"role": "system", "pending": True, "text": text})
        _save_json(SESSION_FILE, self.session_store)


_memory_service = MemoryService()


def get_memory_service() -> MemoryService:
    return _memory_service
