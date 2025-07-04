"""Character management service."""

from typing import Optional, List, Dict
from pathlib import Path

from ..config.logging_config import get_logger
from ..models.character import Character, CharacterRepository

logger = get_logger(__name__)


class CharacterService:
    """Service for managing characters."""
    
    def __init__(self, characters_file: Optional[str] = None):
        """Initialize the character service.
        
        Args:
            characters_file: Path to characters configuration file
        """
        self.repository = CharacterRepository(characters_file)
        logger.info(f"Initialized character service with {len(self.repository.get_all_characters())} characters")
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get a character by ID.
        
        Args:
            character_id: Character identifier
            
        Returns:
            Character instance or None if not found
        """
        return self.repository.get_character(character_id)
    
    def get_all_characters(self) -> List[Character]:
        """Get all available characters.
        
        Returns:
            List of all characters
        """
        return self.repository.get_all_characters()
    
    def get_character_ids(self) -> List[str]:
        """Get all character IDs.
        
        Returns:
            List of character IDs
        """
        return self.repository.get_character_ids()
    
    def get_characters_for_selection(self) -> List[Dict[str, str]]:
        """Get characters formatted for selection menu.
        
        Returns:
            List of character selection data
        """
        characters = self.get_all_characters()
        return [
            {
                "id": char.id,
                "name": char.name,
                "emoji": char.emoji,
                "description": char.description,
                "display_name": f"{char.emoji} {char.name}"
            }
            for char in characters
        ]
    
    def get_character_image_path(self, character_id: str, image_index: int = 0) -> Optional[str]:
        """Get a character image path.
        
        Args:
            character_id: Character identifier
            image_index: Index of the image to get
            
        Returns:
            Image path or None if not found
        """
        character = self.get_character(character_id)
        if not character or not character.image_paths:
            return None
        
        if 0 <= image_index < len(character.image_paths):
            image_path = character.image_paths[image_index]
            # Check if file exists
            if Path(image_path).exists():
                return image_path
            
            logger.warning(f"Image file not found: {image_path}")
        
        return None
    
    def validate_character_images(self) -> Dict[str, List[str]]:
        """Validate that all character images exist.
        
        Returns:
            Dictionary of character_id -> list of missing image paths
        """
        missing_images = {}
        
        for character in self.get_all_characters():
            missing = []
            for image_path in character.image_paths:
                if not Path(image_path).exists():
                    missing.append(image_path)
            
            if missing:
                missing_images[character.id] = missing
        
        return missing_images
    
    def add_character(self, character: Character) -> bool:
        """Add a new character.
        
        Args:
            character: Character to add
            
        Returns:
            True if successful
        """
        try:
            self.repository.add_character(character)
            logger.info(f"Added character {character.id} ({character.name})")
            return True
        except Exception as e:
            logger.error(f"Failed to add character {character.id}: {e}")
            return False
    
    def save_characters(self, file_path: str) -> bool:
        """Save characters to file.
        
        Args:
            file_path: Path to save characters
            
        Returns:
            True if successful
        """
        try:
            self.repository.save_to_file(file_path)
            logger.info(f"Saved characters to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save characters to {file_path}: {e}")
            return False
    
    def reload_characters(self, file_path: str) -> bool:
        """Reload characters from file.
        
        Args:
            file_path: Path to load characters from
            
        Returns:
            True if successful
        """
        try:
            self.repository.load_from_file(file_path)
            logger.info(f"Reloaded characters from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload characters from {file_path}: {e}")
            return False

