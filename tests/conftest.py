"""Pytest configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from pathlib import Path
import sys

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from telegram_ai_bot.config.settings import Settings
from telegram_ai_bot.models.character import Character
from telegram_ai_bot.models.user import User
from telegram_ai_bot.services.assistant_service import AssistantService
from telegram_ai_bot.services.conversation_service import ConversationService
from telegram_ai_bot.services.character_service import CharacterService
from telegram_ai_bot.services.user_service import UserService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    # Set environment variables for testing
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234567890abcdef1234567890abcdef1234567890abcdef")
    
    return Settings(
        telegram_bot_token="123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        openai_api_key="sk-test-key-1234567890abcdef1234567890abcdef1234567890abcdef",
        bot_name="Test Bot",
        bot_username="@test_bot",
        debug=True,
        log_level="DEBUG"
    )


@pytest.fixture
def sample_character():
    """Sample character for testing."""
    return Character(
        id="test_char",
        name="Test Character",
        emoji="🤖",
        description="A test character for unit tests",
        personality="You are a helpful test character.",
        greeting="Hello! I'm a test character.",
        image_paths=["test/image1.jpg", "test/image2.jpg"],
        traits=["helpful", "friendly", "test"],
        conversation_style="helpful and friendly"
    )


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en"
    )


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    
    # Mock assistant creation
    mock_assistant = Mock()
    mock_assistant.id = "asst_test123"
    mock_assistant.name = "Test Assistant"
    mock_assistant.metadata = {"character_id": "test_char"}
    
    client.beta.assistants.create = AsyncMock(return_value=mock_assistant)
    client.beta.assistants.retrieve = AsyncMock(return_value=mock_assistant)
    client.beta.assistants.delete = AsyncMock()
    
    # Mock thread creation
    mock_thread = Mock()
    mock_thread.id = "thread_test123"
    
    client.beta.threads.create = AsyncMock(return_value=mock_thread)
    client.beta.threads.delete = AsyncMock()
    
    # Mock message creation
    mock_message = Mock()
    mock_message.id = "msg_test123"
    
    client.beta.threads.messages.create = AsyncMock(return_value=mock_message)
    
    # Mock run creation and completion
    mock_run = Mock()
    mock_run.id = "run_test123"
    mock_run.status = "completed"
    
    client.beta.threads.runs.create = AsyncMock(return_value=mock_run)
    client.beta.threads.runs.retrieve = AsyncMock(return_value=mock_run)
    
    # Mock messages list
    mock_response_message = Mock()
    mock_response_message.role = "assistant"
    mock_response_message.content = [Mock()]
    mock_response_message.content[0].type = "text"
    mock_response_message.content[0].text.value = "Test response from assistant"
    
    mock_messages = Mock()
    mock_messages.data = [mock_response_message]
    
    client.beta.threads.messages.list = AsyncMock(return_value=mock_messages)
    
    return client


@pytest.fixture
def assistant_service(mock_openai_client, monkeypatch):
    """Assistant service with mocked OpenAI client."""
    service = AssistantService()
    monkeypatch.setattr(service, "client", mock_openai_client)
    return service


@pytest.fixture
def character_service():
    """Character service for testing."""
    return CharacterService()


@pytest.fixture
def user_service():
    """User service for testing."""
    return UserService()


@pytest.fixture
def conversation_service(assistant_service):
    """Conversation service for testing."""
    return ConversationService(assistant_service)


@pytest.fixture
def mock_telegram_update():
    """Mock Telegram update for testing."""
    update = Mock()
    update.effective_user = Mock()
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.effective_user.language_code = "en"
    
    update.message = Mock()
    update.message.text = "Test message"
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    
    update.callback_query = Mock()
    update.callback_query.data = "test_callback"
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    
    return update


@pytest.fixture
def mock_telegram_context():
    """Mock Telegram context for testing."""
    context = Mock()
    context.bot = Mock()
    context.bot.send_chat_action = AsyncMock()
    return context

