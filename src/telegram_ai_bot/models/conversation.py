"""Conversation and message models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class MessageRole(Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Individual message in a conversation."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )
    
    def to_openai_format(self) -> Dict[str, str]:
        """Convert message to OpenAI API format."""
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclass
class Conversation:
    """Conversation model containing messages and metadata."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    character_id: Optional[str] = None
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.
        
        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a user message to the conversation.
        
        Args:
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        message = Message(
            role=MessageRole.USER,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add an assistant message to the conversation.
        
        Args:
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        message = Message(
            role=MessageRole.ASSISTANT,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages from the conversation.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        return self.messages[-limit:] if self.messages else []
    
    def get_openai_messages(self, limit: int = 10, include_system: bool = True) -> List[Dict[str, str]]:
        """Get messages in OpenAI API format.
        
        Args:
            limit: Maximum number of messages to return
            include_system: Whether to include system messages
            
        Returns:
            List of messages in OpenAI format
        """
        recent_messages = self.get_recent_messages(limit)
        
        if include_system and self.character_id:
            # Add system message for character personality
            from ..models.character import CharacterRepository
            char_repo = CharacterRepository()
            character = char_repo.get_character(self.character_id)
            if character:
                system_message = {
                    "role": "system",
                    "content": character.personality
                }
                openai_messages = [system_message]
                openai_messages.extend([msg.to_openai_format() for msg in recent_messages])
                return openai_messages
        
        return [msg.to_openai_format() for msg in recent_messages]
    
    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        self.messages.clear()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "assistant_id": self.assistant_id,
            "thread_id": self.thread_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create conversation from dictionary."""
        messages = [Message.from_dict(msg_data) for msg_data in data.get("messages", [])]
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user_id=data["user_id"],
            character_id=data.get("character_id"),
            assistant_id=data.get("assistant_id"),
            thread_id=data.get("thread_id"),
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )

