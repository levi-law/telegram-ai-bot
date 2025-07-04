"""Message handlers for Telegram bot."""

import re
from telegram import Update
from telegram.ext import ContextTypes

from ..config.logging_config import get_logger
from ..services.conversation_service import ConversationService
from ..services.character_service import CharacterService
from ..services.user_service import UserService

logger = get_logger(__name__)


class MessageHandler:
    """Handler for regular text messages."""
    
    def __init__(
        self,
        conversation_service: ConversationService,
        character_service: CharacterService,
        user_service: UserService
    ):
        """Initialize message handler.
        
        Args:
            conversation_service: Conversation service instance
            character_service: Character service instance
            user_service: User service instance
        """
        self.conversation_service = conversation_service
        self.character_service = character_service
        self.user_service = user_service
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        if not update.message or not update.message.text:
            return
        
        user = update.effective_user
        if not user:
            return
        
        message_text = update.message.text.strip()
        
        # Skip empty messages
        if not message_text:
            return
        
        # Create or update user
        self.user_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code
        )
        
        logger.info(f"Received message from user {user.id}: {message_text[:50]}...")
        
        # Check for photo requests
        if self._is_photo_request(message_text):
            await self._handle_photo_request(update, context)
            return
        
        # Get user session
        session = await self.conversation_service.get_or_create_session(user.id)
        
        # Check if user has selected a character
        if not session.character_id:
            await update.message.reply_text(
                "Hi! 👋 Please select a character first using /start or /characters to begin our conversation!"
            )
            return
        
        # Get character
        character = self.character_service.get_character(session.character_id)
        if not character:
            await update.message.reply_text(
                "❌ Character not found. Please select a character using /characters"
            )
            return
        
        try:
            # Show typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Send message to AI and get response
            response = await self.conversation_service.send_message(user.id, message_text)
            
            if response:
                # Send response to user
                await update.message.reply_text(response)
                logger.info(f"Sent AI response to user {user.id} (character: {character.name})")
            else:
                # Fallback response
                await update.message.reply_text(
                    f"Sorry, {character.name} is having some technical difficulties right now. "
                    f"Please try again in a moment! 🤖"
                )
                logger.warning(f"No AI response generated for user {user.id}")
        
        except Exception as e:
            logger.error(f"Error processing message for user {user.id}: {e}")
            await update.message.reply_text(
                "I'm experiencing some technical issues right now. Please try again later! 🔧"
            )
    
    def _is_photo_request(self, message_text: str) -> bool:
        """Check if the message is requesting a photo.
        
        Args:
            message_text: Message text to check
            
        Returns:
            True if message is requesting a photo
        """
        photo_keywords = [
            "photo", "picture", "pic", "image", "selfie",
            "send me a pic", "show me", "what do you look like",
            "your photo", "your picture", "see you"
        ]
        
        message_lower = message_text.lower()
        return any(keyword in message_lower for keyword in photo_keywords)
    
    async def _handle_photo_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo request messages.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        user = update.effective_user
        if not user:
            return
        
        # Get user session
        session = await self.conversation_service.get_or_create_session(user.id)
        
        if not session.character_id:
            await update.message.reply_text(
                "Please select a character first using /characters"
            )
            return
        
        # Get character and send photo
        character = self.character_service.get_character(session.character_id)
        if not character:
            await update.message.reply_text("❌ Character not found.")
            return
        
        # Get character image
        image_path = self.character_service.get_character_image_path(character.id)
        if not image_path:
            await update.message.reply_text(
                f"Sorry, I don't have any photos available right now! 📸"
            )
            return
        
        try:
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"{character.emoji} Here I am! What do you think?"
                )
            logger.info(f"Sent photo of {character.name} to user {user.id} (via message request)")
        except Exception as e:
            logger.error(f"Failed to send photo for character {character.id}: {e}")
            await update.message.reply_text(
                f"Sorry, I couldn't send my photo right now! 📸❌"
            )

