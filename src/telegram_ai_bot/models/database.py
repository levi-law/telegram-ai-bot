"""
Database models and schema for persistent storage.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from ..config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class UserRecord:
    """User record for database storage."""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserRecord':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class SessionRecord:
    """Session record for database storage."""
    session_id: str
    user_id: int
    character_id: Optional[str]
    assistant_id: Optional[str]
    thread_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionRecord':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: str = "data/bot_sessions.db"):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Database initialized at {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            # Create users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    character_id TEXT,
                    assistant_id TEXT,
                    thread_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_character_id ON sessions(character_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active)")
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def create_or_update_user(self, user_record: UserRecord) -> UserRecord:
        """Create or update user record.
        
        Args:
            user_record: User record to save
            
        Returns:
            Updated user record
        """
        now = datetime.now()
        
        with self._get_connection() as conn:
            # Check if user exists
            existing = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_record.user_id,)
            ).fetchone()
            
            if existing:
                # Update existing user
                user_record.updated_at = now
                conn.execute("""
                    UPDATE users SET
                        username = ?, first_name = ?, last_name = ?,
                        language_code = ?, updated_at = ?, is_active = ?
                    WHERE user_id = ?
                """, (
                    user_record.username, user_record.first_name, user_record.last_name,
                    user_record.language_code, user_record.updated_at.isoformat(),
                    user_record.is_active, user_record.user_id
                ))
                logger.info(f"Updated user {user_record.user_id}")
            else:
                # Create new user
                user_record.created_at = now
                user_record.updated_at = now
                conn.execute("""
                    INSERT INTO users (
                        user_id, username, first_name, last_name,
                        language_code, created_at, updated_at, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_record.user_id, user_record.username, user_record.first_name,
                    user_record.last_name, user_record.language_code,
                    user_record.created_at.isoformat(), user_record.updated_at.isoformat(),
                    user_record.is_active
                ))
                logger.info(f"Created new user {user_record.user_id}")
            
            conn.commit()
            return user_record
    
    def get_user(self, user_id: int) -> Optional[UserRecord]:
        """Get user by ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User record or None if not found
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            
            if row:
                return UserRecord(
                    user_id=row['user_id'],
                    username=row['username'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    language_code=row['language_code'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    is_active=bool(row['is_active'])
                )
            return None
    
    def create_or_update_session(self, session_record: SessionRecord) -> SessionRecord:
        """Create or update session record.
        
        Args:
            session_record: Session record to save
            
        Returns:
            Updated session record
        """
        now = datetime.now()
        
        with self._get_connection() as conn:
            # Check if session exists
            existing = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_record.session_id,)
            ).fetchone()
            
            metadata_json = json.dumps(session_record.metadata) if session_record.metadata else None
            
            if existing:
                # Update existing session
                session_record.updated_at = now
                session_record.last_activity = now
                conn.execute("""
                    UPDATE sessions SET
                        character_id = ?, assistant_id = ?, thread_id = ?,
                        updated_at = ?, last_activity = ?, is_active = ?, metadata = ?
                    WHERE session_id = ?
                """, (
                    session_record.character_id, session_record.assistant_id,
                    session_record.thread_id, session_record.updated_at.isoformat(),
                    session_record.last_activity.isoformat(), session_record.is_active,
                    metadata_json, session_record.session_id
                ))
                logger.info(f"Updated session {session_record.session_id}")
            else:
                # Create new session
                session_record.created_at = now
                session_record.updated_at = now
                session_record.last_activity = now
                conn.execute("""
                    INSERT INTO sessions (
                        session_id, user_id, character_id, assistant_id, thread_id,
                        created_at, updated_at, last_activity, is_active, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_record.session_id, session_record.user_id,
                    session_record.character_id, session_record.assistant_id,
                    session_record.thread_id, session_record.created_at.isoformat(),
                    session_record.updated_at.isoformat(), session_record.last_activity.isoformat(),
                    session_record.is_active, metadata_json
                ))
                logger.info(f"Created new session {session_record.session_id}")
            
            conn.commit()
            return session_record
    
    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session record or None if not found
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            
            if row:
                metadata = json.loads(row['metadata']) if row['metadata'] else None
                return SessionRecord(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    character_id=row['character_id'],
                    assistant_id=row['assistant_id'],
                    thread_id=row['thread_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    last_activity=datetime.fromisoformat(row['last_activity']),
                    is_active=bool(row['is_active']),
                    metadata=metadata
                )
            return None
    
    def get_user_sessions(self, user_id: int, active_only: bool = True) -> List[SessionRecord]:
        """Get all sessions for a user.
        
        Args:
            user_id: Telegram user ID
            active_only: Only return active sessions
            
        Returns:
            List of session records
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM sessions WHERE user_id = ?"
            params = [user_id]
            
            if active_only:
                query += " AND is_active = 1"
            
            query += " ORDER BY last_activity DESC"
            
            rows = conn.execute(query, params).fetchall()
            
            sessions = []
            for row in rows:
                metadata = json.loads(row['metadata']) if row['metadata'] else None
                sessions.append(SessionRecord(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    character_id=row['character_id'],
                    assistant_id=row['assistant_id'],
                    thread_id=row['thread_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    last_activity=datetime.fromisoformat(row['last_activity']),
                    is_active=bool(row['is_active']),
                    metadata=metadata
                ))
            
            return sessions
    
    def deactivate_user_sessions(self, user_id: int) -> None:
        """Deactivate all sessions for a user.
        
        Args:
            user_id: Telegram user ID
        """
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET is_active = 0, updated_at = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user_id)
            )
            conn.commit()
            logger.info(f"Deactivated all sessions for user {user_id}")
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old inactive sessions.
        
        Args:
            days: Number of days to keep sessions
            
        Returns:
            Number of sessions cleaned up
        """
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE is_active = 0 AND updated_at < ?",
                (cutoff_date.isoformat(),)
            )
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old sessions")
            
            return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database stats
        """
        with self._get_connection() as conn:
            stats = {}
            
            # User stats
            stats['total_users'] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            stats['active_users'] = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0]
            
            # Session stats
            stats['total_sessions'] = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            stats['active_sessions'] = conn.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1").fetchone()[0]
            
            # Character usage stats
            character_stats = conn.execute("""
                SELECT character_id, COUNT(*) as count 
                FROM sessions 
                WHERE character_id IS NOT NULL 
                GROUP BY character_id 
                ORDER BY count DESC
            """).fetchall()
            stats['character_usage'] = {row[0]: row[1] for row in character_stats}
            
            return stats

