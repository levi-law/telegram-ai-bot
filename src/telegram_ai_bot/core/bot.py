"""Core Telegram bot implementation."""

import asyncio
from typing import Optional
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from ..config.logging_config import get_logger
from ..config.settings import Settings
from ..services.assistant_service import AssistantService
from ..services.conversation_service import ConversationService
from ..services.character_service import CharacterService
from ..services.user_service import UserService
from ..handlers.command_handler import CommandHandler as BotCommandHandler
from ..handlers.message_handler import MessageHandler as BotMessageHandler
from ..handlers.callback_handler import CallbackHandler

logger = get_logger(__name__)


class TelegramAIBot:
    """Main Telegram AI Bot class."""
    
    def __init__(self, settings: Settings):
        """Initialize the bot.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.application: Optional[Application] = None
        
        # Initialize services
        self.assistant_service = AssistantService()
        self.character_service = CharacterService()
        self.user_service = UserService()
        self.conversation_service = ConversationService(self.assistant_service)
        
        # Initialize handlers
        self.command_handler = BotCommandHandler(
            self.conversation_service,
            self.character_service,
            self.user_service
        )
        self.message_handler = BotMessageHandler(
            self.conversation_service,
            self.character_service,
            self.user_service
        )
        self.callback_handler = CallbackHandler(
            self.conversation_service,
            self.character_service,
            self.user_service
        )
        
        logger.info("TelegramAIBot initialized")
    
    async def initialize(self) -> None:
        """Initialize the bot application."""
        # Create application
        self.application = Application.builder().token(self.settings.telegram_bot_token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.command_handler.start_command))
        self.application.add_handler(CommandHandler("characters", self.command_handler.characters_command))
        self.application.add_handler(CommandHandler("startover", self.command_handler.startover_command))
        self.application.add_handler(CommandHandler("photo", self.command_handler.photo_command))
        self.application.add_handler(CommandHandler("status", self.command_handler.status_command))
        self.application.add_handler(CommandHandler("help", self.command_handler.help_command))
        
        # Add callback handler
        self.application.add_handler(CallbackQueryHandler(self.callback_handler.handle_callback))
        
        # Add message handler (for non-command messages)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler.handle_message)
        )
        
        # Initialize application
        await self.application.initialize()
        
        logger.info("Bot application initialized")
    
    async def start(self) -> None:
        """Start the bot."""
        if not self.application:
            await self.initialize()
        
        logger.info("Starting Telegram AI Bot...")
        
        # Start the application
        await self.application.start()
        
        # Start polling
        await self.application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
        logger.info("Bot started and polling for updates")
    
    async def stop(self) -> None:
        """Stop the bot."""
        if not self.application:
            return
        
        logger.info("Stopping Telegram AI Bot...")
        
        # Stop polling
        await self.application.updater.stop()
        
        # Stop application
        await self.application.stop()
        
        # Shutdown
        await self.application.shutdown()
        
        logger.info("Bot stopped")
    
    async def run(self) -> None:
        """Run the bot until interrupted."""
        try:
            await self.start()
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            raise
        finally:
            await self.stop()
    
    def get_stats(self) -> dict:
        """Get bot statistics.
        
        Returns:
            Dictionary with bot statistics
        """
        return {
            "active_sessions": self.conversation_service.get_active_sessions_count(),
            "total_conversations": self.conversation_service.get_total_conversations_count(),
            "total_users": self.user_service.get_user_count(),
            "available_characters": len(self.character_service.get_all_characters())
        }
    
    async def cleanup(self) -> None:
        """Perform cleanup operations."""
        logger.info("Performing bot cleanup...")
        
        # Cleanup expired sessions
        expired_sessions = self.conversation_service.cleanup_expired_sessions(
            self.settings.session_timeout
        )
        if expired_sessions > 0:
            logger.info(f"Cleaned up {expired_sessions} expired sessions")
        
        # Cleanup assistants if needed
        # Note: Be careful with this in production
        # deleted_assistants = await self.assistant_service.cleanup_assistants()
        # if deleted_assistants > 0:
        #     logger.info(f"Cleaned up {deleted_assistants} assistants")
        
        logger.info("Cleanup completed")

