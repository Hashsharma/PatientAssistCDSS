import json
import datetime 
from pathlib import Path

AUDIT_FILE = Path("data/audit_logs.jsonl")

def log_interaction(query: str, response: str, sources: list, latency: float):
    """Append interaction to immutable audit log."""
    AUDIT_FILE.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "query": query,
        "response_summary": response[:100] + "...",
        "sources_cited": sources,
        "latency": latency
    }
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")