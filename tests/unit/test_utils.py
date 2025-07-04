"""Tests for utility functions."""

import pytest
from datetime import datetime
from telegram_ai_bot.utils.helpers import (
    format_timestamp, sanitize_text, truncate_text, 
    escape_markdown, extract_user_mention, is_valid_url
)
from telegram_ai_bot.utils.validators import (
    validate_telegram_id, validate_character_id, validate_message_content,
    validate_username, validate_language_code, validate_openai_api_key,
    validate_telegram_token
)


class TestHelpers:
    """Tests for helper functions."""
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2023, 12, 25, 15, 30, 45)
        formatted = format_timestamp(dt)
        assert formatted == "2023-12-25 15:30:45"
        
        # Test custom format
        formatted_custom = format_timestamp(dt, "%Y-%m-%d")
        assert formatted_custom == "2023-12-25"
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        # Test control character removal with actual control characters
        text_with_control = "Hello\x00World\x1f"  # Actual control characters
        sanitized = sanitize_text(text_with_control)
        assert sanitized == "HelloWorld"
        
        # Test whitespace stripping
        text_with_whitespace = "  Hello World  "
        sanitized = sanitize_text(text_with_whitespace)
        assert sanitized == "Hello World"
        
        # Test length truncation
        long_text = "A" * 100
        sanitized = sanitize_text(long_text, max_length=10)
        assert len(sanitized) == 10
        assert sanitized.endswith("...")
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs truncation"
        truncated = truncate_text(text, 20)
        assert len(truncated) == 20
        assert truncated.endswith("...")
        
        # Test text shorter than limit
        short_text = "Short"
        truncated = truncate_text(short_text, 20)
        assert truncated == "Short"
    
    def test_escape_markdown(self):
        """Test markdown escaping."""
        text = "Hello *world* [link](url)"
        escaped = escape_markdown(text)
        assert "\\*" in escaped
        assert "\\[" in escaped
        assert "\\]" in escaped
    
    def test_extract_user_mention(self):
        """Test user mention extraction."""
        text_with_mention = "Hello @username how are you?"
        username = extract_user_mention(text_with_mention)
        assert username == "username"
        
        text_without_mention = "Hello there"
        username = extract_user_mention(text_without_mention)
        assert username is None
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://localhost:8080")
        assert is_valid_url("https://api.openai.com/v1/chat")
        assert not is_valid_url("not-a-url")
        assert not is_valid_url("ftp://example.com")


class TestValidators:
    """Tests for validator functions."""
    
    def test_validate_telegram_id(self):
        """Test Telegram ID validation."""
        assert validate_telegram_id(123456789)
        assert not validate_telegram_id(-123)
        assert not validate_telegram_id(0)
        assert not validate_telegram_id("123456789")
        assert not validate_telegram_id(None)
    
    def test_validate_character_id(self):
        """Test character ID validation."""
        assert validate_character_id("riley")
        assert validate_character_id("test_character")
        assert validate_character_id("char123")
        assert not validate_character_id("Riley")  # uppercase
        assert not validate_character_id("123char")  # starts with number
        assert not validate_character_id("char-name")  # hyphen not allowed
        assert not validate_character_id("")  # empty
        assert not validate_character_id(123)  # not string
    
    def test_validate_message_content(self):
        """Test message content validation."""
        assert validate_message_content("Hello world")
        assert validate_message_content("A" * 4000)  # max length
        assert not validate_message_content("")  # empty
        assert not validate_message_content("   ")  # whitespace only
        assert not validate_message_content("A" * 4001)  # too long
        assert not validate_message_content(123)  # not string
    
    def test_validate_username(self):
        """Test username validation."""
        assert validate_username("username")
        assert validate_username("user_name")
        assert validate_username("user123")
        assert validate_username("a" * 32)  # max length
        assert not validate_username("user")  # too short
        assert not validate_username("user__name")  # consecutive underscores
        assert not validate_username("123user")  # starts with number
        assert not validate_username("user-name")  # hyphen not allowed
        assert not validate_username("a" * 33)  # too long
    
    def test_validate_language_code(self):
        """Test language code validation."""
        assert validate_language_code("en")
        assert validate_language_code("en-us")
        assert validate_language_code("fr-ca")
        assert validate_language_code("EN")  # uppercase is converted to lowercase
        assert not validate_language_code("english")  # too long
        assert not validate_language_code("en_us")  # underscore not allowed
        assert not validate_language_code("123")  # numbers not allowed
    
    def test_validate_openai_api_key(self):
        """Test OpenAI API key validation."""
        valid_key = "sk-" + "a" * 48
        assert validate_openai_api_key(valid_key)
        
        assert not validate_openai_api_key("invalid-key")
        assert not validate_openai_api_key("sk-short")
        assert not validate_openai_api_key("ak-" + "a" * 48)  # wrong prefix
        assert not validate_openai_api_key(123)  # not string
    
    def test_validate_telegram_token(self):
        """Test Telegram bot token validation."""
        valid_token = "123456789:" + "A" * 35  # Exactly 35 characters
        assert validate_telegram_token(valid_token)
        
        assert not validate_telegram_token("invalid-token")
        assert not validate_telegram_token("123456789:short")
        assert not validate_telegram_token("notanumber:" + "A" * 35)
        assert not validate_telegram_token(123)  # not string

