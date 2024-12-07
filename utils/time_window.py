import re
from datetime import timedelta

def parse_time_window(window_str: str) -> timedelta:
    """
    Parse a time window string into a timedelta object.
    Supports formats:
    - 'd' for days (e.g., '30d')
    - 'h' for hours (e.g., '24h')
    - 'm' for minutes (e.g., '30m')
    
    Args:
        window_str: String representing time window (e.g., '30d', '24h', '30m')
        
    Returns:
        timedelta object representing the time window
        
    Raises:
        ValueError: If the format is invalid
    """
    if not window_str:
        raise ValueError("Time window string cannot be empty")
    
    pattern = re.compile(r'^(\d+)([dhm])$')
    match = pattern.match(window_str)
    
    if not match:
        raise ValueError(
            "Invalid time window format. Use format: "
            "NUMBER followed by 'd' (days), 'h' (hours), or 'm' (minutes). "
            "Examples: '30d', '24h', '30m'"
        )
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    else:
        raise ValueError(f"Invalid time unit: {unit}")

def time_window_to_seconds(window: timedelta) -> int:
    """Convert a timedelta window to seconds"""
    return int(window.total_seconds())
