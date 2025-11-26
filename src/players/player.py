"""Abstract base class for Go game players."""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.board import Board


class Player(ABC):
    """Abstract base class representing a Go player."""
    
    def __init__(self, color: str):
        """
        Initialize player.
        
        Args:
            color: Player's stone color ('black' or 'white')
        """
        self.color = color
    
    @abstractmethod
    def get_move(self, board: 'Board') -> Optional[Tuple[int, int]]:
        """
        Get the player's next move.
        
        Args:
            board: Current board state
            
        Returns:
            Move as (row, col) tuple, or None for pass
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color})"
