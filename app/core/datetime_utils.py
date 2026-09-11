# app/core/datetime_utils.py
from datetime import datetime, timezone

def utc_now() -> datetime:
    """Return naive UTC datetime (Python 3.12+ compliant, zero deprecation warnings)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
