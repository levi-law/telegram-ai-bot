"""User management service."""

from typing import Optional, Dict, List
from datetime import datetime

from ..config.logging_config import get_logger
from ..models.user import User

logger = get_logger(__name__)


class UserService:
    """Service for managing users."""
    
    def __init__(self):
        """Initialize the user service."""
        self._users: Dict[int, User] = {}  # telegram_id -> user
    
    def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> User:
        """Get or create a user.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code
            
        Returns:
            User instance
        """
        if telegram_id in self._users:
            user = self._users[telegram_id]
            # Update user information if provided
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if language_code and user.language_code != language_code:
                user.language_code = language_code
                updated = True
            
            if updated:
                user.updated_at = datetime.utcnow()
                logger.info(f"Updated user {telegram_id} information")
            
            return user
        
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code
        )
        self._users[telegram_id] = user
        logger.info(f"Created new user {telegram_id} ({user.full_name})")
        return user
    
    def get_user(self, telegram_id: int) -> Optional[User]:
        """Get a user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User instance or None if not found
        """
        return self._users.get(telegram_id)
    
    def update_user_metadata(self, telegram_id: int, metadata: Dict) -> bool:
        """Update user metadata.
        
        Args:
            telegram_id: Telegram user ID
            metadata: Metadata to update
            
        Returns:
            True if successful
        """
        user = self.get_user(telegram_id)
        if not user:
            return False
        
        user.metadata.update(metadata)
        user.updated_at = datetime.utcnow()
        logger.info(f"Updated metadata for user {telegram_id}")
        return True
    
    def get_all_users(self) -> List[User]:
        """Get all users.
        
        Returns:
            List of all users
        """
        return list(self._users.values())
    
    def get_user_count(self) -> int:
        """Get the total number of users.
        
        Returns:
            Number of users
        """
        return len(self._users)
    
    def get_users_by_language(self, language_code: str) -> List[User]:
        """Get users by language code.
        
        Args:
            language_code: Language code to filter by
            
        Returns:
            List of users with the specified language
        """
        return [
            user for user in self._users.values()
            if user.language_code == language_code
        ]
    
    def delete_user(self, telegram_id: int) -> bool:
        """Delete a user.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if user was deleted
        """
        if telegram_id in self._users:
            del self._users[telegram_id]
            logger.info(f"Deleted user {telegram_id}")
            return True
        return False

