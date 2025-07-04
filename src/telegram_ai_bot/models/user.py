"""User and session models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class User:
    """User model for Telegram users."""
    
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.username or f"User {self.telegram_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user from dictionary."""
        return cls(
            telegram_id=data["telegram_id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            language_code=data.get("language_code"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class UserSession:
    """User session model for managing conversation state."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    character_id: Optional[str] = None
    conversation_id: Optional[str] = None
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def set_character(self, character_id: str) -> None:
        """Set the active character for this session.
        
        Args:
            character_id: Character identifier
        """
        self.character_id = character_id
        self.update_activity()
    
    def set_conversation(self, conversation_id: str) -> None:
        """Set the active conversation for this session.
        
        Args:
            conversation_id: Conversation identifier
        """
        self.conversation_id = conversation_id
        self.update_activity()
    
    def set_assistant_thread(self, assistant_id: str, thread_id: str) -> None:
        """Set the OpenAI Assistant and Thread IDs.
        
        Args:
            assistant_id: OpenAI Assistant ID
            thread_id: OpenAI Thread ID
        """
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.update_activity()
    
    def reset(self) -> None:
        """Reset the session state."""
        self.character_id = None
        self.conversation_id = None
        self.assistant_id = None
        self.thread_id = None
        self.update_activity()
    
    def is_expired(self, timeout_seconds: int = 3600) -> bool:
        """Check if the session has expired.
        
        Args:
            timeout_seconds: Session timeout in seconds
            
        Returns:
            True if session has expired
        """
        if not self.is_active:
            return True
        
        time_diff = datetime.utcnow() - self.last_activity
        return time_diff.total_seconds() > timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "conversation_id": self.conversation_id,
            "assistant_id": self.assistant_id,
            "thread_id": self.thread_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create session from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user_id=data["user_id"],
            character_id=data.get("character_id"),
            conversation_id=data.get("conversation_id"),
            assistant_id=data.get("assistant_id"),
            thread_id=data.get("thread_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            is_active=data.get("is_active", True),
            metadata=data.get("metadata", {})
        )

