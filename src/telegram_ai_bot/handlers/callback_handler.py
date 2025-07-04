"""Callback handlers for Telegram bot inline keyboards."""

from telegram import Update
from telegram.ext import ContextTypes

from ..config.logging_config import get_logger
from ..services.conversation_service import ConversationService
from ..services.character_service import CharacterService
from ..services.user_service import UserService

logger = get_logger(__name__)


class CallbackHandler:
    """Handler for inline keyboard callbacks."""
    
    def __init__(
        self,
        conversation_service: ConversationService,
        character_service: CharacterService,
        user_service: UserService
    ):
        """Initialize callback handler.
        
        Args:
            conversation_service: Conversation service instance
            character_service: Character service instance
            user_service: User service instance
        """
        self.conversation_service = conversation_service
        self.character_service = character_service
        self.user_service = user_service
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline keyboards.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        query = update.callback_query
        if not query or not query.data:
            return
        
        user = query.from_user
        if not user:
            return
        
        # Parse callback data
        callback_data = query.data
        
        try:
            if callback_data.startswith("select_character:"):
                await self._handle_character_selection(query, callback_data)
            else:
                logger.warning(f"Unknown callback data: {callback_data}")
                await query.answer("Unknown action")
        
        except Exception as e:
            logger.error(f"Error handling callback {callback_data}: {e}")
            await query.answer("An error occurred. Please try again.")
    
    async def _handle_character_selection(self, query, callback_data: str) -> None:
        """Handle character selection callback.
        
        Args:
            query: Callback query
            callback_data: Callback data string
        """
        # Extract character ID
        character_id = callback_data.split(":", 1)[1]
        user = query.from_user
        
        # Get character
        character = self.character_service.get_character(character_id)
        if not character:
            await query.answer("Character not found")
            return
        
        try:
            # Set character for user
            session = await self.conversation_service.set_character(user.id, character)
            
            # Update the message
            await query.edit_message_text(
                f"✅ **Character Selected: {character.emoji} {character.name}**\\n\\n"
                f"{character.description}\\n\\n"
                f"💬 {character.greeting}\\n\\n"
                f"You can now start chatting! I'll respond as {character.name}.",
                parse_mode='Markdown'
            )
            
            await query.answer(f"Selected {character.name}")
            
            logger.info(f"User {user.id} selected character {character.id} ({character.name})")
            
        except Exception as e:
            logger.error(f"Failed to set character {character_id} for user {user.id}: {e}")
            await query.answer("Failed to select character. Please try again.")
            await query.edit_message_text(
                "❌ Failed to select character. Please try /characters again."
            )

