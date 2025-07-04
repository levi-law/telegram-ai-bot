"""Main application class for Telegram AI Bot."""

import asyncio
import signal
import sys
from typing import Optional

from ..config.logging_config import setup_logging, get_logger
from ..config.settings import get_settings
from .bot import TelegramAIBot

logger = get_logger(__name__)


class Application:
    """Main application class that manages the bot lifecycle."""
    
    def __init__(self):
        """Initialize the application."""
        self.settings = get_settings()
        self.bot: Optional[TelegramAIBot] = None
        self._shutdown_event = asyncio.Event()
        
        # Setup logging
        setup_logging(
            log_level=self.settings.log_level,
            log_file="telegram_ai_bot.log"
        )
        
        logger.info("Application initialized")
    
    async def startup(self) -> None:
        """Perform application startup."""
        logger.info("Starting Telegram AI Bot application...")
        
        # Validate settings
        self._validate_settings()
        
        # Initialize bot
        self.bot = TelegramAIBot(self.settings)
        await self.bot.initialize()
        
        logger.info("Application startup completed")
    
    async def shutdown(self) -> None:
        """Perform application shutdown."""
        logger.info("Shutting down application...")
        
        if self.bot:
            await self.bot.cleanup()
            await self.bot.stop()
        
        logger.info("Application shutdown completed")
    
    async def run(self) -> None:
        """Run the application."""
        try:
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Startup
            await self.startup()
            
            # Start bot
            if self.bot:
                await self.bot.start()
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self.shutdown()
    
    def _validate_settings(self) -> None:
        """Validate application settings."""
        if not self.settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        logger.info("Settings validation passed")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            asyncio.create_task(self._trigger_shutdown())
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, signal_handler)
        
        logger.info("Signal handlers setup completed")
    
    async def _trigger_shutdown(self) -> None:
        """Trigger application shutdown."""
        logger.info("Triggering application shutdown...")
        self._shutdown_event.set()


async def main() -> None:
    """Main entry point for the application."""
    app = Application()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())

