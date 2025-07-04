"""Tests for handler classes."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram_ai_bot.handlers.command_handler import CommandHandler
from telegram_ai_bot.handlers.message_handler import MessageHandler
from telegram_ai_bot.handlers.callback_handler import CallbackHandler


class TestCommandHandler:
    """Tests for CommandHandler."""
    
    @pytest.fixture
    def command_handler(self, conversation_service, character_service, user_service):
        """Create command handler for testing."""
        return CommandHandler(conversation_service, character_service, user_service)
    
    @pytest.mark.asyncio
    async def test_start_command(self, command_handler, mock_telegram_update, mock_telegram_context):
        """Test /start command."""
        await command_handler.start_command(mock_telegram_update, mock_telegram_context)
        
        # Should reply with character selection
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args
        assert "Choose your AI character" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_characters_command(self, command_handler, mock_telegram_update, mock_telegram_context):
        """Test /characters command."""
        await command_handler.characters_command(mock_telegram_update, mock_telegram_context)
        
        # Should show character selection
        mock_telegram_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_startover_command(self, command_handler, mock_telegram_update, mock_telegram_context):
        """Test /startover command."""
        await command_handler.startover_command(mock_telegram_update, mock_telegram_context)
        
        # Should reply with reset confirmation
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args
        assert "reset" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_help_command(self, command_handler, mock_telegram_update, mock_telegram_context):
        """Test /help command."""
        await command_handler.help_command(mock_telegram_update, mock_telegram_context)
        
        # Should reply with help text
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args
        assert "Commands:" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_status_command(self, command_handler, mock_telegram_update, mock_telegram_context):
        """Test /status command."""
        await command_handler.status_command(mock_telegram_update, mock_telegram_context)
        
        # Should reply with status
        mock_telegram_update.message.reply_text.assert_called_once()


class TestMessageHandler:
    """Tests for MessageHandler."""
    
    @pytest.fixture
    def message_handler(self, conversation_service, character_service, user_service):
        """Create message handler for testing."""
        return MessageHandler(conversation_service, character_service, user_service)
    
    @pytest.mark.asyncio
    async def test_handle_message_no_character(self, message_handler, mock_telegram_update, mock_telegram_context):
        """Test handling message when no character is selected."""
        await message_handler.handle_message(mock_telegram_update, mock_telegram_context)
        
        # Should ask user to select character
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args
        assert "select a character" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_handle_message_with_character(
        self, 
        message_handler, 
        mock_telegram_update, 
        mock_telegram_context,
        sample_character
    ):
        """Test handling message with character selected."""
        # Set up character first
        await message_handler.conversation_service.set_character(123456789, sample_character)
        
        await message_handler.handle_message(mock_telegram_update, mock_telegram_context)
        
        # Should send AI response
        mock_telegram_update.message.reply_text.assert_called_once()
    
    def test_is_photo_request(self, message_handler):
        """Test photo request detection."""
        assert message_handler._is_photo_request("send me a photo")
        assert message_handler._is_photo_request("show me your picture")
        assert message_handler._is_photo_request("what do you look like")
        assert not message_handler._is_photo_request("hello there")
    
    @pytest.mark.asyncio
    async def test_handle_photo_request(
        self, 
        message_handler, 
        mock_telegram_update, 
        mock_telegram_context,
        sample_character
    ):
        """Test handling photo request."""
        # Set up character
        await message_handler.conversation_service.set_character(123456789, sample_character)
        
        # Mock image file existence
        with patch('builtins.open', mock=Mock()):
            with patch('pathlib.Path.exists', return_value=True):
                await message_handler._handle_photo_request(mock_telegram_update, mock_telegram_context)
        
        # Should send photo
        mock_telegram_update.message.reply_photo.assert_called_once()


class TestCallbackHandler:
    """Tests for CallbackHandler."""
    
    @pytest.fixture
    def callback_handler(self, conversation_service, character_service, user_service):
        """Create callback handler for testing."""
        return CallbackHandler(conversation_service, character_service, user_service)
    
    @pytest.mark.asyncio
    async def test_handle_character_selection(
        self, 
        callback_handler, 
        mock_telegram_update, 
        mock_telegram_context
    ):
        """Test character selection callback."""
        # Set up callback query
        mock_telegram_update.callback_query.data = "select_character:riley"
        
        await callback_handler.handle_callback(mock_telegram_update, mock_telegram_context)
        
        # Should answer callback and edit message
        mock_telegram_update.callback_query.answer.assert_called_once()
        mock_telegram_update.callback_query.edit_message_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_unknown_callback(
        self, 
        callback_handler, 
        mock_telegram_update, 
        mock_telegram_context
    ):
        """Test unknown callback handling."""
        # Set up unknown callback
        mock_telegram_update.callback_query.data = "unknown_action:test"
        
        await callback_handler.handle_callback(mock_telegram_update, mock_telegram_context)
        
        # Should answer with unknown action
        mock_telegram_update.callback_query.answer.assert_called_once_with("Unknown action")

