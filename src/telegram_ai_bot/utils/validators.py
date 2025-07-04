"""Validation utility functions."""

import re
from typing import Any


def validate_telegram_id(telegram_id: Any) -> bool:
    """Validate Telegram user ID.
    
    Args:
        telegram_id: ID to validate
        
    Returns:
        True if valid Telegram ID
    """
    if not isinstance(telegram_id, int):
        return False
    
    # Telegram user IDs are positive integers
    return telegram_id > 0


def validate_character_id(character_id: Any) -> bool:
    """Validate character ID format.
    
    Args:
        character_id: Character ID to validate
        
    Returns:
        True if valid character ID
    """
    if not isinstance(character_id, str):
        return False
    
    # Character IDs should be lowercase alphanumeric with underscores
    pattern = r'^[a-z][a-z0-9_]*$'
    return bool(re.match(pattern, character_id)) and len(character_id) <= 50


def validate_message_content(content: Any) -> bool:
    """Validate message content.
    
    Args:
        content: Message content to validate
        
    Returns:
        True if valid message content
    """
    if not isinstance(content, str):
        return False
    
    # Message should not be empty and not too long
    return 0 < len(content.strip()) <= 4000


def validate_username(username: Any) -> bool:
    """Validate Telegram username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid username format
    """
    if not isinstance(username, str):
        return False
    
    # Telegram usernames: 5-32 chars, alphanumeric + underscore, no consecutive underscores
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$'
    
    if not re.match(pattern, username):
        return False
    
    # Check for consecutive underscores
    return '__' not in username


def validate_language_code(language_code: Any) -> bool:
    """Validate language code format.
    
    Args:
        language_code: Language code to validate
        
    Returns:
        True if valid language code
    """
    if not isinstance(language_code, str):
        return False
    
    # ISO 639-1 language codes (2 letters) or with country code (2-2 letters)
    pattern = r'^[a-z]{2}(-[a-z]{2})?$'
    return bool(re.match(pattern, language_code.lower()))


def validate_openai_api_key(api_key: Any) -> bool:
    """Validate OpenAI API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid API key format
    """
    if not isinstance(api_key, str):
        return False
    
    # OpenAI API keys start with 'sk-' and are followed by alphanumeric characters
    pattern = r'^sk-[a-zA-Z0-9]{48,}$'
    return bool(re.match(pattern, api_key))


def validate_telegram_token(token: Any) -> bool:
    """Validate Telegram bot token format.
    
    Args:
        token: Bot token to validate
        
    Returns:
        True if valid bot token format
    """
    if not isinstance(token, str):
        return False
    
    # Telegram bot tokens: bot_id:auth_token (numbers:alphanumeric)
    pattern = r'^\d+:[a-zA-Z0-9_-]{35}$'
    return bool(re.match(pattern, token))

