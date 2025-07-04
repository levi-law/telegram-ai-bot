"""Tests for data models."""

import pytest
from datetime import datetime
from telegram_ai_bot.models.character import Character, CharacterRepository
from telegram_ai_bot.models.conversation import Conversation, Message, MessageRole
from telegram_ai_bot.models.user import User, UserSession


class TestCharacter:
    """Tests for Character model."""
    
    def test_character_creation(self, sample_character):
        """Test character creation."""
        assert sample_character.id == "test_char"
        assert sample_character.name == "Test Character"
        assert sample_character.emoji == "🤖"
        assert "helpful" in sample_character.traits
    
    def test_character_to_dict(self, sample_character):
        """Test character serialization."""
        data = sample_character.to_dict()
        assert data["id"] == "test_char"
        assert data["name"] == "Test Character"
        assert isinstance(data["traits"], list)
    
    def test_character_from_dict(self, sample_character):
        """Test character deserialization."""
        data = sample_character.to_dict()
        new_character = Character.from_dict(data)
        assert new_character.id == sample_character.id
        assert new_character.name == sample_character.name


class TestCharacterRepository:
    """Tests for CharacterRepository."""
    
    def test_repository_initialization(self):
        """Test repository initialization with default characters."""
        repo = CharacterRepository()
        characters = repo.get_all_characters()
        assert len(characters) > 0
        assert any(char.id == "riley" for char in characters)
    
    def test_get_character(self):
        """Test getting character by ID."""
        repo = CharacterRepository()
        character = repo.get_character("riley")
        assert character is not None
        assert character.name == "Riley"
    
    def test_add_character(self, sample_character):
        """Test adding a character."""
        repo = CharacterRepository()
        repo.add_character(sample_character)
        retrieved = repo.get_character("test_char")
        assert retrieved is not None
        assert retrieved.name == "Test Character"


class TestMessage:
    """Tests for Message model."""
    
    def test_message_creation(self):
        """Test message creation."""
        message = Message(
            role=MessageRole.USER,
            content="Test message"
        )
        assert message.role == MessageRole.USER
        assert message.content == "Test message"
        assert isinstance(message.timestamp, datetime)
    
    def test_message_to_openai_format(self):
        """Test message OpenAI format conversion."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Assistant response"
        )
        openai_format = message.to_openai_format()
        assert openai_format["role"] == "assistant"
        assert openai_format["content"] == "Assistant response"
    
    def test_message_serialization(self):
        """Test message serialization and deserialization."""
        message = Message(
            role=MessageRole.USER,
            content="Test content"
        )
        data = message.to_dict()
        new_message = Message.from_dict(data)
        assert new_message.role == message.role
        assert new_message.content == message.content


class TestConversation:
    """Tests for Conversation model."""
    
    def test_conversation_creation(self):
        """Test conversation creation."""
        conversation = Conversation(user_id=123456789)
        assert conversation.user_id == 123456789
        assert len(conversation.messages) == 0
        assert isinstance(conversation.created_at, datetime)
    
    def test_add_user_message(self):
        """Test adding user message."""
        conversation = Conversation(user_id=123456789)
        message = conversation.add_user_message("Hello")
        assert len(conversation.messages) == 1
        assert message.role == MessageRole.USER
        assert message.content == "Hello"
    
    def test_add_assistant_message(self):
        """Test adding assistant message."""
        conversation = Conversation(user_id=123456789)
        message = conversation.add_assistant_message("Hi there!")
        assert len(conversation.messages) == 1
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Hi there!"
    
    def test_get_recent_messages(self):
        """Test getting recent messages."""
        conversation = Conversation(user_id=123456789)
        
        # Add multiple messages
        for i in range(5):
            conversation.add_user_message(f"Message {i}")
        
        recent = conversation.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[-1].content == "Message 4"  # Most recent
    
    def test_clear_messages(self):
        """Test clearing messages."""
        conversation = Conversation(user_id=123456789)
        conversation.add_user_message("Test")
        assert len(conversation.messages) == 1
        
        conversation.clear_messages()
        assert len(conversation.messages) == 0


class TestUser:
    """Tests for User model."""
    
    def test_user_creation(self, sample_user):
        """Test user creation."""
        assert sample_user.telegram_id == 123456789
        assert sample_user.username == "testuser"
        assert sample_user.first_name == "Test"
    
    def test_user_full_name(self, sample_user):
        """Test user full name property."""
        assert sample_user.full_name == "Test User"
        
        # Test with only first name
        user = User(telegram_id=123, first_name="John")
        assert user.full_name == "John"
        
        # Test with no names
        user = User(telegram_id=123, username="johndoe")
        assert user.full_name == "johndoe"
    
    def test_user_serialization(self, sample_user):
        """Test user serialization."""
        data = sample_user.to_dict()
        new_user = User.from_dict(data)
        assert new_user.telegram_id == sample_user.telegram_id
        assert new_user.username == sample_user.username


class TestUserSession:
    """Tests for UserSession model."""
    
    def test_session_creation(self):
        """Test session creation."""
        session = UserSession(user_id=123456789)
        assert session.user_id == 123456789
        assert session.is_active is True
        assert session.character_id is None
    
    def test_set_character(self):
        """Test setting character."""
        session = UserSession(user_id=123456789)
        session.set_character("riley")
        assert session.character_id == "riley"
    
    def test_session_expiry(self):
        """Test session expiry check."""
        session = UserSession(user_id=123456789)
        
        # Fresh session should not be expired
        assert not session.is_expired(timeout_seconds=3600)
        
        # Inactive session should be expired
        session.is_active = False
        assert session.is_expired(timeout_seconds=3600)
    
    def test_session_reset(self):
        """Test session reset."""
        session = UserSession(user_id=123456789)
        session.set_character("riley")
        session.set_conversation("conv_123")
        
        session.reset()
        assert session.character_id is None
        assert session.conversation_id is None

