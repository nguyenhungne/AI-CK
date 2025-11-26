"""Human player implementation for Go game."""
from typing import Tuple, Optional, TYPE_CHECKING
from src.players.player import Player

if TYPE_CHECKING:
    from src.models.board import Board


class HumanPlayer(Player):
    """Human player that receives moves from UI input."""
    
    def __init__(self, color: str):
        """Initialize human player."""
        super().__init__(color)
        self.pending_move: Optional[Tuple[int, int]] = None
    
    def get_move(self, board: 'Board') -> Optional[Tuple[int, int]]:
        """
        Get move from pending input.
        
        Returns:
            Pending move if set, None otherwise
        """
        move = self.pending_move
        self.pending_move = None
        return move
    
    def set_move(self, row: int, col: int) -> None:
        """
        Set the pending move from UI input.
        
        Args:
            row: Row position
            col: Column position
        """
        self.pending_move = (row, col)
    
    def clear_move(self) -> None:
        """Clear any pending move."""
        self.pending_move = None
