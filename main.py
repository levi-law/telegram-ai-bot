#!/usr/bin/env python3
"""
Main entry point for Telegram AI Bot.

This script starts the Telegram AI Bot application with proper error handling
and logging configuration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from telegram_ai_bot.core.application import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

