"""Conversation management service."""

from typing import Optional, Dict, Any
from datetime import datetime

from ..config.logging_config import get_logger
from ..models.conversation import Conversation, Message, MessageRole
from ..models.user import UserSession
from ..models.character import Character
from ..services.assistant_service import AssistantService

logger = get_logger(__name__)


class ConversationService:
    """Service for managing conversations and user sessions."""
    
    def __init__(self, assistant_service: AssistantService):
        """Initialize the conversation service.
        
        Args:
            assistant_service: Assistant service instance
        """
        self.assistant_service = assistant_service
        self._sessions: Dict[int, UserSession] = {}  # user_id -> session
        self._conversations: Dict[str, Conversation] = {}  # conversation_id -> conversation
    
    async def get_or_create_session(self, user_id: int) -> UserSession:
        """Get or create a user session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User session
        """
        if user_id in self._sessions:
            session = self._sessions[user_id]
            session.update_activity()
            return session
        
        # Create new session
        session = UserSession(user_id=user_id)
        self._sessions[user_id] = session
        logger.info(f"Created new session for user {user_id}")
        return session
    
    async def set_character(self, user_id: int, character: Character) -> UserSession:
        """Set the active character for a user session.
        
        Args:
            user_id: Telegram user ID
            character: Character to set
            
        Returns:
            Updated user session
        """
        session = await self.get_or_create_session(user_id)
        
        # If changing character, reset the conversation
        if session.character_id != character.id:
            await self.reset_conversation(user_id)
            
            # Get or create assistant for character
            assistant_id = await self.assistant_service.get_or_create_assistant(character)
            
            # Create new thread
            thread_id = await self.assistant_service.create_thread(
                assistant_id=assistant_id,
                user_id=user_id,
                character_id=character.id
            )
            
            # Update session
            session.set_character(character.id)
            session.set_assistant_thread(assistant_id, thread_id)
            
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                character_id=character.id,
                assistant_id=assistant_id,
                thread_id=thread_id
            )
            self._conversations[conversation.id] = conversation
            session.set_conversation(conversation.id)
            
            logger.info(f"Set character {character.id} for user {user_id}")
        
        return session
    
    async def send_message(self, user_id: int, message_text: str) -> Optional[str]:
        """Send a message and get response.
        
        Args:
            user_id: Telegram user ID
            message_text: User message text
            
        Returns:
            Assistant response or None if no character selected
        """
        session = await self.get_or_create_session(user_id)
        
        if not session.character_id or not session.assistant_id or not session.thread_id:
            logger.warning(f"User {user_id} has no active character/assistant")
            return None
        
        try:
            # Get conversation
            conversation = self._conversations.get(session.conversation_id)
            if not conversation:
                logger.error(f"Conversation {session.conversation_id} not found for user {user_id}")
                return None
            
            # Add user message to conversation
            conversation.add_user_message(message_text)
            
            # Send to assistant and get response
            response = await self.assistant_service.send_message(
                thread_id=session.thread_id,
                assistant_id=session.assistant_id,
                message=message_text,
                user_id=user_id
            )
            
            # Add assistant response to conversation
            conversation.add_assistant_message(response)
            
            # Update session activity
            session.update_activity()
            
            logger.info(f"Processed message for user {user_id}, response length: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process message for user {user_id}: {e}")
            return None
    
    async def reset_conversation(self, user_id: int) -> bool:
        """Reset the conversation for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        session = await self.get_or_create_session(user_id)
        
        try:
            # Delete existing thread if exists
            if session.thread_id:
                await self.assistant_service.delete_thread(session.thread_id)
            
            # Remove conversation from memory
            if session.conversation_id and session.conversation_id in self._conversations:
                del self._conversations[session.conversation_id]
            
            # Reset session
            character_id = session.character_id  # Keep character
            session.reset()
            session.character_id = character_id  # Restore character
            
            logger.info(f"Reset conversation for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset conversation for user {user_id}: {e}")
            return False
    
    async def get_conversation_history(self, user_id: int, limit: int = 10) -> Optional[Conversation]:
        """Get conversation history for a user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages to return
            
        Returns:
            Conversation with recent messages or None
        """
        session = await self.get_or_create_session(user_id)
        
        if not session.conversation_id:
            return None
        
        conversation = self._conversations.get(session.conversation_id)
        if not conversation:
            return None
        
        # Create a copy with limited messages
        limited_conversation = Conversation(
            id=conversation.id,
            user_id=conversation.user_id,
            character_id=conversation.character_id,
            assistant_id=conversation.assistant_id,
            thread_id=conversation.thread_id,
            messages=conversation.get_recent_messages(limit),
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            metadata=conversation.metadata
        )
        
        return limited_conversation
    
    def get_session_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session information for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session information dictionary or None
        """
        if user_id not in self._sessions:
            return None
        
        session = self._sessions[user_id]
        conversation = self._conversations.get(session.conversation_id)
        
        return {
            "session_id": session.id,
            "character_id": session.character_id,
            "conversation_id": session.conversation_id,
            "assistant_id": session.assistant_id,
            "thread_id": session.thread_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "is_active": session.is_active,
            "message_count": len(conversation.messages) if conversation else 0
        }
    
    def cleanup_expired_sessions(self, timeout_seconds: int = 3600) -> int:
        """Clean up expired sessions.
        
        Args:
            timeout_seconds: Session timeout in seconds
            
        Returns:
            Number of sessions cleaned up
        """
        expired_users = []
        
        for user_id, session in self._sessions.items():
            if session.is_expired(timeout_seconds):
                expired_users.append(user_id)
        
        cleaned_count = 0
        for user_id in expired_users:
            try:
                session = self._sessions[user_id]
                
                # Remove conversation
                if session.conversation_id and session.conversation_id in self._conversations:
                    del self._conversations[session.conversation_id]
                
                # Remove session
                del self._sessions[user_id]
                cleaned_count += 1
                
                logger.info(f"Cleaned up expired session for user {user_id}")
                
            except Exception as e:
                logger.error(f"Failed to cleanup session for user {user_id}: {e}")
        
        return cleaned_count
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions.
        
        Returns:
            Number of active sessions
        """
        return len([s for s in self._sessions.values() if s.is_active])
    
    def get_total_conversations_count(self) -> int:
        """Get the total number of conversations.
        
        Returns:
            Number of conversations
        """
        return len(self._conversations)

