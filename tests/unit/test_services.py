"""Tests for service classes."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram_ai_bot.services.assistant_service import AssistantService
from telegram_ai_bot.services.conversation_service import ConversationService
from telegram_ai_bot.services.character_service import CharacterService
from telegram_ai_bot.services.user_service import UserService


class TestAssistantService:
    """Tests for AssistantService."""
    
    @pytest.mark.asyncio
    async def test_get_or_create_assistant(self, assistant_service, sample_character):
        """Test getting or creating an assistant."""
        assistant_id = await assistant_service.get_or_create_assistant(sample_character)
        assert assistant_id == "asst_test123"
        
        # Should use cache on second call
        assistant_id_2 = await assistant_service.get_or_create_assistant(sample_character)
        assert assistant_id_2 == assistant_id
    
    @pytest.mark.asyncio
    async def test_create_thread(self, assistant_service):
        """Test creating a thread."""
        thread_id = await assistant_service.create_thread(
            assistant_id="asst_test123",
            user_id=123456789,
            character_id="test_char"
        )
        assert thread_id == "thread_test123"
    
    @pytest.mark.asyncio
    async def test_send_message(self, assistant_service):
        """Test sending a message to assistant."""
        response = await assistant_service.send_message(
            thread_id="thread_test123",
            assistant_id="asst_test123",
            message="Hello",
            user_id=123456789
        )
        assert response == "Test response from assistant"
    
    @pytest.mark.asyncio
    async def test_delete_thread(self, assistant_service):
        """Test deleting a thread."""
        result = await assistant_service.delete_thread("thread_test123")
        assert result is True


class TestConversationService:
    """Tests for ConversationService."""
    
    @pytest.mark.asyncio
    async def test_get_or_create_session(self, conversation_service):
        """Test getting or creating a session."""
        session = await conversation_service.get_or_create_session(123456789)
        assert session.user_id == 123456789
        
        # Should return same session on second call
        session_2 = await conversation_service.get_or_create_session(123456789)
        assert session.id == session_2.id
    
    @pytest.mark.asyncio
    async def test_set_character(self, conversation_service, sample_character):
        """Test setting character for a session."""
        session = await conversation_service.set_character(123456789, sample_character)
        assert session.character_id == sample_character.id
        assert session.assistant_id is not None
        assert session.thread_id is not None
    
    @pytest.mark.asyncio
    async def test_send_message(self, conversation_service, sample_character):
        """Test sending a message."""
        # First set a character
        await conversation_service.set_character(123456789, sample_character)
        
        # Then send a message
        response = await conversation_service.send_message(123456789, "Hello")
        assert response == "Test response from assistant"
    
    @pytest.mark.asyncio
    async def test_reset_conversation(self, conversation_service, sample_character):
        """Test resetting a conversation."""
        # Set character and send message
        await conversation_service.set_character(123456789, sample_character)
        await conversation_service.send_message(123456789, "Hello")
        
        # Reset conversation
        result = await conversation_service.reset_conversation(123456789)
        assert result is True
    
    def test_cleanup_expired_sessions(self, conversation_service):
        """Test cleaning up expired sessions."""
        # Create a session and mark it as expired
        session = conversation_service._sessions[123456789] = Mock()
        session.is_expired.return_value = True
        
        cleaned = conversation_service.cleanup_expired_sessions(timeout_seconds=1)
        assert cleaned == 1
        assert 123456789 not in conversation_service._sessions


class TestCharacterService:
    """Tests for CharacterService."""
    
    def test_get_character(self, character_service):
        """Test getting a character."""
        character = character_service.get_character("riley")
        assert character is not None
        assert character.name == "Riley"
    
    def test_get_all_characters(self, character_service):
        """Test getting all characters."""
        characters = character_service.get_all_characters()
        assert len(characters) > 0
        assert any(char.id == "riley" for char in characters)
    
    def test_get_characters_for_selection(self, character_service):
        """Test getting characters for selection menu."""
        selection_data = character_service.get_characters_for_selection()
        assert len(selection_data) > 0
        assert all("id" in char and "display_name" in char for char in selection_data)
    
    def test_add_character(self, character_service, sample_character):
        """Test adding a character."""
        result = character_service.add_character(sample_character)
        assert result is True
        
        retrieved = character_service.get_character("test_char")
        assert retrieved is not None
        assert retrieved.name == "Test Character"
    
    @patch('pathlib.Path.exists')
    def test_get_character_image_path(self, mock_exists, character_service, sample_character):
        """Test getting character image path."""
        mock_exists.return_value = True
        character_service.add_character(sample_character)
        
        image_path = character_service.get_character_image_path("test_char", 0)
        assert image_path == "test/image1.jpg"
    
    @patch('pathlib.Path.exists')
    def test_validate_character_images(self, mock_exists, character_service, sample_character):
        """Test validating character images."""
        mock_exists.return_value = False  # Simulate missing files
        character_service.add_character(sample_character)
        
        missing = character_service.validate_character_images()
        assert "test_char" in missing
        assert len(missing["test_char"]) == 2  # Both images missing


class TestUserService:
    """Tests for UserService."""
    
    def test_get_or_create_user(self, user_service):
        """Test getting or creating a user."""
        user = user_service.get_or_create_user(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        
        # Should return same user on second call
        user_2 = user_service.get_or_create_user(telegram_id=123456789)
        assert user.telegram_id == user_2.telegram_id
    
    def test_update_user_metadata(self, user_service):
        """Test updating user metadata."""
        user = user_service.get_or_create_user(telegram_id=123456789)
        
        result = user_service.update_user_metadata(123456789, {"test_key": "test_value"})
        assert result is True
        assert user.metadata["test_key"] == "test_value"
    
    def test_get_user_count(self, user_service):
        """Test getting user count."""
        initial_count = user_service.get_user_count()
        
        user_service.get_or_create_user(telegram_id=123456789)
        user_service.get_or_create_user(telegram_id=987654321)
        
        assert user_service.get_user_count() == initial_count + 2
    
    def test_get_users_by_language(self, user_service):
        """Test getting users by language."""
        user_service.get_or_create_user(telegram_id=123456789, language_code="en")
        user_service.get_or_create_user(telegram_id=987654321, language_code="es")
        
        en_users = user_service.get_users_by_language("en")
        assert len(en_users) == 1
        assert en_users[0].telegram_id == 123456789
    
    def test_delete_user(self, user_service):
        """Test deleting a user."""
        user_service.get_or_create_user(telegram_id=123456789)
        
        result = user_service.delete_user(123456789)
        assert result is True
        
        user = user_service.get_user(123456789)
        assert user is None

