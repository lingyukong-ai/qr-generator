"""Global history management for QR code generation."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# Global history directory
HISTORY_DIR = Path.home() / ".qr-generator"
HISTORY_FILE = HISTORY_DIR / "history.json"


def _ensure_history_dir() -> None:
    """Ensure the history directory exists."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _load_history() -> dict[str, Any]:
    """Load history from file.
    
    Returns:
        History dictionary with 'entries' list.
    """
    _ensure_history_dir()
    
    if not HISTORY_FILE.exists():
        return {"entries": []}
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "entries" not in data:
                data["entries"] = []
            return data
    except (json.JSONDecodeError, IOError):
        return {"entries": []}


def _save_history(history: dict[str, Any]) -> None:
    """Save history to file.
    
    Args:
        history: History dictionary to save.
    """
    _ensure_history_dir()
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_entry(
    qr_type: str,
    command: str,
    output_path: str,
    data: Optional[dict[str, Any]] = None,
) -> str:
    """Add a new entry to history.
    
    Args:
        qr_type: The type of QR code (url, text, wifi, etc.).
        command: The full command used to generate the QR code.
        output_path: The path where the QR code was saved.
        data: Optional dictionary of data used for generation.
        
    Returns:
        The ID of the new entry.
    """
    history = _load_history()
    
    entry_id = str(uuid.uuid4())[:8]
    entry = {
        "id": entry_id,
        "type": qr_type,
        "command": command,
        "output_path": output_path,
        "data": data or {},
        "created_at": datetime.now().isoformat(),
    }
    
    history["entries"].append(entry)
    _save_history(history)
    
    return entry_id


def get_entries(limit: Optional[int] = None) -> list[dict[str, Any]]:
    """Get history entries.
    
    Args:
        limit: Maximum number of entries to return (most recent first).
        
    Returns:
        List of history entries.
    """
    history = _load_history()
    entries = history["entries"]
    
    # Sort by created_at descending (most recent first)
    entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    if limit:
        entries = entries[:limit]
    
    return entries


def get_entry(entry_id: str) -> Optional[dict[str, Any]]:
    """Get a specific history entry by ID.
    
    Args:
        entry_id: The entry ID to look up.
        
    Returns:
        The entry dictionary, or None if not found.
    """
    history = _load_history()
    
    for entry in history["entries"]:
        if entry.get("id") == entry_id:
            return entry
    
    return None


def clear_history() -> int:
    """Clear all history entries.
    
    Returns:
        The number of entries that were cleared.
    """
    history = _load_history()
    count = len(history["entries"])
    
    history["entries"] = []
    _save_history(history)
    
    return count


def format_entry_for_display(entry: dict[str, Any], index: int) -> str:
    """Format a history entry for display.
    
    Args:
        entry: The history entry.
        index: The display index (1-based).
        
    Returns:
        Formatted string for display.
    """
    created_at = entry.get("created_at", "unknown")
    qr_type = entry.get("type", "unknown")
    command = entry.get("command", "")
    
    # Format timestamp
    try:
        dt = datetime.fromisoformat(created_at)
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        timestamp = created_at
    
    # Mask sensitive data in command
    masked_command = _mask_sensitive_data(command)
    
    return f"[{index}] {timestamp} - {qr_type}\n    {masked_command}"


def _mask_sensitive_data(command: str) -> str:
    """Mask sensitive data in command string.
    
    Args:
        command: The command string.
        
    Returns:
        Command with passwords masked.
    """
    import re
    
    # Mask WiFi passwords
    masked = re.sub(
        r'(--password\s+["\']?)([^"\'\s]+)(["\']?)',
        r'\1****\3',
        command,
    )
    
    return masked

