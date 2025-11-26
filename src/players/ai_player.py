"""AI player implementation using Minimax algorithm."""
from typing import Tuple, Optional, TYPE_CHECKING
from src.players.player import Player
from src.ai.minimax import MinimaxAI

if TYPE_CHECKING:
    from src.models.board import Board


class AIPlayer(Player):
    """AI player using Heuristic Minimax Search."""
    
    def __init__(self, color: str, depth_limit: Optional[int] = None):
        """
        Initialize AI player.
        
        Args:
            color: Player's stone color
            depth_limit: Fixed depth limit, or None for adaptive
        """
        super().__init__(color)
        self.ai = MinimaxAI(depth_limit)
        self.captured_stones = 0
        self.opponent_captured = 0
    
    def get_move(self, board: 'Board') -> Optional[Tuple[int, int]]:
        """
        Calculate best move using Minimax algorithm.
        
        Args:
            board: Current board state
            
        Returns:
            Best move as (row, col) tuple, or None if no valid moves
        """
        return self.ai.find_best_move(
            board, self.color,
            self.captured_stones, self.opponent_captured
        )
    
    def update_captures(self, captured_by_ai: int, captured_by_opponent: int) -> None:
        """Update capture counts for heuristic evaluation."""
        self.captured_stones = captured_by_ai
        self.opponent_captured = captured_by_opponent
