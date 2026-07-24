import json
import os
from datetime import datetime

LOG_DIR = "logs"
TRACE_FILE = os.path.join(LOG_DIR, "trace.jsonl")

def init_trace():
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(TRACE_FILE, "w", encoding="utf-8") as f:
        pass  # Очищаємо файл для нового запуску

def log_trace(event_type: str, data: dict):
    """Логує крок у форматі JSONL з підтримкою складних типів даних."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data
    }
    
    # default=str гарантує, що datetime, UUID або Decimal з API не зламають JSON
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")