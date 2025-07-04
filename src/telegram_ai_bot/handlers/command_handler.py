"""Command handlers for Telegram bot."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..config.logging_config import get_logger
from ..services.conversation_service import ConversationService
from ..services.character_service import CharacterService
from ..services.user_service import UserService

logger = get_logger(__name__)


class CommandHandler:
    """Handler for bot commands."""
    
    def __init__(
        self,
        conversation_service: ConversationService,
        character_service: CharacterService,
        user_service: UserService
    ):
        """Initialize command handler.
        
        Args:
            conversation_service: Conversation service instance
            character_service: Character service instance
            user_service: User service instance
        """
        self.conversation_service = conversation_service
        self.character_service = character_service
        self.user_service = user_service
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        user = update.effective_user
        if not user:
            return
        
        # Create or update user
        self.user_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code
        )
        
        logger.info(f"User {user.id} started the bot")
        
        # Show character selection
        await self._show_character_selection(update, context)
    
    async def characters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /characters command.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        await self._show_character_selection(update, context)
    
    async def startover_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /startover command.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        user = update.effective_user
        if not user:
            return
        
        # Reset conversation
        success = await self.conversation_service.reset_conversation(user.id)
        
        if success:
            await update.message.reply_text(
                "🔄 Conversation reset! Your chat history has been cleared.\\n"
                "You can continue chatting with the same character or select a new one with /characters"
            )
            logger.info(f"Reset conversation for user {user.id}")
        else:
            await update.message.reply_text(
                "❌ Failed to reset conversation. Please try again."
            )
    
    async def photo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /photo command.
        
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
                f"Sorry, I don't have any photos of {character.name} available right now."
            )
            return
        
        try:
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"{character.emoji} Here's a photo of {character.name}!"
                )
            logger.info(f"Sent photo of {character.name} to user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send photo for character {character.id}: {e}")
            await update.message.reply_text(
                f"Sorry, I couldn't send the photo of {character.name} right now."
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        user = update.effective_user
        if not user:
            return
        
        # Get session info
        session_info = self.conversation_service.get_session_info(user.id)
        
        if not session_info:
            await update.message.reply_text("No active session found.")
            return
        
        # Get character info
        character_name = "None"
        if session_info["character_id"]:
            character = self.character_service.get_character(session_info["character_id"])
            if character:
                character_name = f"{character.emoji} {character.name}"
        
        status_text = f"""
📊 **Your Status**

👤 **Character**: {character_name}
💬 **Messages**: {session_info['message_count']}
🕐 **Session Started**: {session_info['created_at'][:19]}
⏰ **Last Activity**: {session_info['last_activity'][:19]}
✅ **Status**: {'Active' if session_info['is_active'] else 'Inactive'}
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        help_text = """
🤖 **AI Bot Help**

**Commands:**
/start - Start the bot and select a character
/characters - Show character selection menu
/photo - Get a photo of your current character
/startover - Reset conversation and start fresh
/status - Show your current status
/help - Show this help message

**How to use:**
1. Use /start to begin
2. Select a character from the menu
3. Start chatting! The AI will respond as your chosen character
4. Use /startover to reset your conversation anytime
5. Use /characters to switch to a different character

**Features:**
✨ Real AI conversations with unique personalities
🎭 Multiple characters to choose from
💭 Conversation memory within each session
📸 Character photos on request
🔄 Easy conversation reset

Enjoy chatting with our AI characters!
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _show_character_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show character selection menu.
        
        Args:
            update: Telegram update
            context: Bot context
        """
        characters = self.character_service.get_characters_for_selection()
        
        if not characters:
            await update.message.reply_text("No characters available.")
            return
        
        # Create inline keyboard
        keyboard = []
        for char in characters:
            keyboard.append([
                InlineKeyboardButton(
                    text=char["display_name"],
                    callback_data=f"select_character:{char['id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎭 **Choose your AI character:**\\n\\n"
            "Each character has a unique personality and conversation style. "
            "Select one to start chatting!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

