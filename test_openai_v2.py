#!/usr/bin/env python3
"""
Test script to verify OpenAI Assistant API v2 is working.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from telegram_ai_bot.services.assistant_service import AssistantService
from telegram_ai_bot.services.character_service import CharacterService
from telegram_ai_bot.config.settings import get_settings

async def test_openai_v2():
    """Test OpenAI Assistant API v2."""
    print("🧪 Testing OpenAI Assistant API v2...")
    
    try:
        # Initialize services
        settings = get_settings()
        print(f"✅ Settings loaded - API key: {settings.openai_api_key[:10]}...")
        
        assistant_service = AssistantService()
        print("✅ Assistant service initialized")
        
        character_service = CharacterService("assets/data/characters.json")
        characters = character_service.get_all_characters()
        print(f"✅ Character service initialized - {len(characters)} characters loaded")
        
        if not characters:
            print("❌ No characters found!")
            return False
        
        # Test with first character
        test_character = characters[0]
        print(f"🧪 Testing with character: {test_character.name} ({test_character.id})")
        
        # Try to create assistant
        assistant_id = await assistant_service.get_or_create_assistant(test_character)
        print(f"✅ Assistant created successfully: {assistant_id}")
        
        # Try to create thread
        thread_id = await assistant_service.create_thread(
            assistant_id=assistant_id,
            user_id=12345,
            character_id=test_character.id
        )
        print(f"✅ Thread created successfully: {thread_id}")
        
        print("🎉 OpenAI Assistant API v2 is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI API: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai_v2())
    sys.exit(0 if result else 1)

