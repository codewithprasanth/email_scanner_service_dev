import uuid
from datetime import datetime

def build_scan_name(user_email: str, folder_name: str) -> str:
    short_id = uuid.uuid4().hex[:6].upper()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"SCAN | {folder_name} | {user_email} | {timestamp} | #{short_id}"
