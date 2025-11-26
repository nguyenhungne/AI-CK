"""Game state and move data models for Go game."""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class Move:
    """Represents a single move in the game."""
    row: int
    col: int
    color: str
    is_pass: bool = False
    
    def __repr__(self) -> str:
        if self.is_pass:
            return f"Move(pass, {self.color})"
        return f"Move({self.row}, {self.col}, {self.color})"


@dataclass
class GameState:
    """Tracks the complete state of a Go game."""
    current_player: str = 'black'
    captured_black: int = 0  # Black stones captured by white
    captured_white: int = 0  # White stones captured by black
    move_history: List[Move] = field(default_factory=list)
    consecutive_passes: int = 0
    ko_position: Optional[int] = None  # Hash of board state for Ko rule
    game_over: bool = False
    winner: Optional[str] = None
    resigned: bool = False
    
    def switch_player(self) -> None:
        """Switch to the other player."""
        self.current_player = 'white' if self.current_player == 'black' else 'black'
    
    def add_move(self, move: Move) -> None:
        """Add a move to history."""
        self.move_history.append(move)
        if move.is_pass:
            self.consecutive_passes += 1
        else:
            self.consecutive_passes = 0
    
    def add_captures(self, color: str, count: int) -> None:
        """Add captured stones count."""
        if color == 'black':
            self.captured_black += count
        else:
            self.captured_white += count
    
    def get_opponent(self, color: str) -> str:
        """Get the opponent's color."""
        return 'white' if color == 'black' else 'black'
    
    def reset(self) -> None:
        """Reset game state for a new game."""
        self.current_player = 'black'
        self.captured_black = 0
        self.captured_white = 0
        self.move_history = []
        self.consecutive_passes = 0
        self.ko_position = None
        self.game_over = False
        self.winner = None
        self.resigned = False
