"""OpenAI Assistant API service for conversation management."""

import asyncio
from typing import Optional, Dict, Any, List
import openai
from openai import OpenAI

from ..config.logging_config import get_logger
from ..config.settings import get_settings
from ..models.assistant import Assistant, AssistantThread
from ..models.character import Character

logger = get_logger(__name__)


class AssistantService:
    """Service for managing OpenAI Assistants and conversations."""
    
    def __init__(self):
        """Initialize the Assistant service."""
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self._assistants_cache: Dict[str, str] = {}  # character_id -> assistant_id
        
    async def get_or_create_assistant(self, character: Character) -> str:
        """Get or create an OpenAI Assistant for a character.
        
        Args:
            character: Character to create assistant for
            
        Returns:
            Assistant ID
        """
        # Check cache first
        if character.id in self._assistants_cache:
            assistant_id = self._assistants_cache[character.id]
            try:
                # Verify assistant still exists
                await self._get_assistant(assistant_id)
                return assistant_id
            except Exception as e:
                logger.warning(f"Cached assistant {assistant_id} not found: {e}")
                del self._assistants_cache[character.id]
        
        # Create new assistant
        try:
            assistant = await self._create_assistant(character)
            self._assistants_cache[character.id] = assistant.id
            logger.info(f"Created assistant {assistant.id} for character {character.id}")
            return assistant.id
        except Exception as e:
            logger.error(f"Failed to create assistant for character {character.id}: {e}")
            raise
    
    async def create_thread(self, assistant_id: str, user_id: int, character_id: str) -> str:
        """Create a new conversation thread.
        
        Args:
            assistant_id: OpenAI Assistant ID
            user_id: Telegram user ID
            character_id: Character ID
            
        Returns:
            Thread ID
        """
        try:
            thread = await asyncio.to_thread(
                self.client.beta.threads.create,
                metadata={
                    "user_id": str(user_id),
                    "character_id": character_id,
                    "assistant_id": assistant_id
                }
            )
            logger.info(f"Created thread {thread.id} for user {user_id} with character {character_id}")
            return thread.id
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            raise
    
    async def send_message(
        self, 
        thread_id: str, 
        assistant_id: str, 
        message: str,
        user_id: int
    ) -> str:
        """Send a message and get response from assistant.
        
        Args:
            thread_id: OpenAI Thread ID
            assistant_id: OpenAI Assistant ID
            message: User message
            user_id: Telegram user ID
            
        Returns:
            Assistant response
        """
        try:
            # Add user message to thread
            await asyncio.to_thread(
                self.client.beta.threads.messages.create,
                thread_id=thread_id,
                role="user",
                content=message,
                metadata={"user_id": str(user_id)}
            )
            
            # Create and wait for run completion
            run = await asyncio.to_thread(
                self.client.beta.threads.runs.create,
                thread_id=thread_id,
                assistant_id=assistant_id,
                metadata={"user_id": str(user_id)}
            )
            
            # Wait for completion
            response = await self._wait_for_run_completion(thread_id, run.id)
            logger.info(f"Generated response for user {user_id} in thread {thread_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to send message to assistant: {e}")
            raise
    
    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a conversation thread.
        
        Args:
            thread_id: Thread ID to delete
            
        Returns:
            True if successful
        """
        try:
            await asyncio.to_thread(
                self.client.beta.threads.delete,
                thread_id=thread_id
            )
            logger.info(f"Deleted thread {thread_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete thread {thread_id}: {e}")
            return False
    
    async def _create_assistant(self, character: Character) -> Any:
        """Create a new OpenAI Assistant for a character.
        
        Args:
            character: Character to create assistant for
            
        Returns:
            OpenAI Assistant object
        """
        return await asyncio.to_thread(
            self.client.beta.assistants.create,
            name=f"{character.name} - {character.description}",
            instructions=character.personality,
            model=self.settings.openai_model,
            metadata={
                "character_id": character.id,
                "character_name": character.name,
                "bot_version": "1.0.0"
            }
        )
    
    async def _get_assistant(self, assistant_id: str) -> Any:
        """Get an OpenAI Assistant by ID.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            OpenAI Assistant object
        """
        return await asyncio.to_thread(
            self.client.beta.assistants.retrieve,
            assistant_id=assistant_id
        )
    
    async def _wait_for_run_completion(self, thread_id: str, run_id: str, timeout: int = 30) -> str:
        """Wait for a run to complete and return the response.
        
        Args:
            thread_id: Thread ID
            run_id: Run ID
            timeout: Timeout in seconds
            
        Returns:
            Assistant response text
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Run {run_id} timed out after {timeout} seconds")
            
            # Get run status
            run = await asyncio.to_thread(
                self.client.beta.threads.runs.retrieve,
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run.status == "completed":
                # Get the latest assistant message
                messages = await asyncio.to_thread(
                    self.client.beta.threads.messages.list,
                    thread_id=thread_id,
                    limit=1
                )
                
                if messages.data:
                    message = messages.data[0]
                    if message.role == "assistant" and message.content:
                        # Extract text content
                        for content in message.content:
                            if content.type == "text":
                                return content.text.value
                
                raise ValueError("No assistant response found")
            
            elif run.status in ["failed", "cancelled", "expired"]:
                raise RuntimeError(f"Run {run_id} failed with status: {run.status}")
            
            # Wait before checking again
            await asyncio.sleep(1)
    
    async def list_assistants(self) -> List[Dict[str, Any]]:
        """List all assistants created by this bot.
        
        Returns:
            List of assistant information
        """
        try:
            assistants = await asyncio.to_thread(
                self.client.beta.assistants.list,
                limit=100
            )
            
            bot_assistants = []
            for assistant in assistants.data:
                if assistant.metadata and assistant.metadata.get("bot_version"):
                    bot_assistants.append({
                        "id": assistant.id,
                        "name": assistant.name,
                        "character_id": assistant.metadata.get("character_id"),
                        "created_at": assistant.created_at
                    })
            
            return bot_assistants
        except Exception as e:
            logger.error(f"Failed to list assistants: {e}")
            return []
    
    async def cleanup_assistants(self) -> int:
        """Clean up unused assistants.
        
        Returns:
            Number of assistants deleted
        """
        try:
            assistants = await self.list_assistants()
            deleted_count = 0
            
            for assistant_info in assistants:
                try:
                    await asyncio.to_thread(
                        self.client.beta.assistants.delete,
                        assistant_id=assistant_info["id"]
                    )
                    deleted_count += 1
                    logger.info(f"Deleted assistant {assistant_info['id']}")
                except Exception as e:
                    logger.warning(f"Failed to delete assistant {assistant_info['id']}: {e}")
            
            # Clear cache
            self._assistants_cache.clear()
            
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup assistants: {e}")
            return 0

