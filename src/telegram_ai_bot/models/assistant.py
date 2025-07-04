"""OpenAI Assistant and Thread models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


@dataclass
class Assistant:
    """OpenAI Assistant model."""
    
    id: str
    name: str
    description: str
    instructions: str
    model: str = "gpt-3.5-turbo"
    tools: List[Dict[str, Any]] = field(default_factory=list)
    file_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assistant to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "model": self.model,
            "tools": self.tools,
            "file_ids": self.file_ids,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assistant":
        """Create assistant from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            instructions=data["instructions"],
            model=data.get("model", "gpt-3.5-turbo"),
            tools=data.get("tools", []),
            file_ids=data.get("file_ids", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()))
        )


@dataclass
class AssistantThread:
    """OpenAI Assistant Thread model."""
    
    id: str
    assistant_id: str
    user_id: int
    character_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert thread to dictionary."""
        return {
            "id": self.id,
            "assistant_id": self.assistant_id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssistantThread":
        """Create thread from dictionary."""
        return cls(
            id=data["id"],
            assistant_id=data["assistant_id"],
            user_id=data["user_id"],
            character_id=data.get("character_id"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            metadata=data.get("metadata", {})
        )

