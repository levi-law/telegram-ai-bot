"""
Telegram AI Bot - Professional AI-powered Telegram bot with OpenAI Assistant API integration.

A production-ready Python package for creating intelligent Telegram bots with
multiple character personalities and advanced conversation management.
"""

__version__ = "1.0.0"
__author__ = "Telegram AI Bot Team"
__email__ = "support@telegram-ai-bot.com"

from .core.bot import TelegramAIBot
from .core.application import Application

__all__ = ["TelegramAIBot", "Application"]

