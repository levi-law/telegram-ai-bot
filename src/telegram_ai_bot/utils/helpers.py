"""Helper utility functions."""

import re
from datetime import datetime
from typing import Optional


def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a timestamp to string.
    
    Args:
        timestamp: Datetime object to format
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    return timestamp.strftime(format_str)


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize text for safe display.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        Sanitized text
    """
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """Escape markdown special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def extract_user_mention(text: str) -> Optional[str]:
    """Extract username mention from text.
    
    Args:
        text: Text to search for mentions
        
    Returns:
        Username without @ or None if not found
    """
    match = re.search(r'@(\w+)', text)
    return match.group(1) if match else None


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

