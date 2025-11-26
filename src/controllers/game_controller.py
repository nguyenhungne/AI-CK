"""Game controller for managing Go game flow and state."""
from typing import Dict, Optional, Tuple, Callable
from src.models.board import Board
from src.models.game_state import GameState, Move


class GameController:
    """Orchestrates game flow, manages turns, and coordinates game logic."""
    
    def __init__(self, mode: str = 'human_vs_human'):
        """Initialize game controller."""
        self.mode = mode
        self.board = Board(9)
        self.state = GameState()
        self.on_state_change: Optional[Callable] = None
    
    def start_game(self) -> None:
        """Start or restart the game."""
        self.board = Board(9)
        self.state.reset()
        if self.on_state_change:
            self.on_state_change()
    
    def make_move(self, row: int, col: int) -> bool:
        """Attempt to make a move. Returns True if successful."""
        if self.state.game_over:
            return False
        
        color = self.state.current_player
        
        # Validate move
        if not self.board.is_valid_move(row, col, color, self.state.ko_position):
            return False
        
        # Store previous hash for Ko rule
        prev_hash = self.board.board_hash()
        
        # Place stone
        self.board.place_stone(row, col, color)
        
        # Process captures
        opponent = self.state.get_opponent(color)
        captured = self.board.find_captured_stones(opponent)
        self.board.remove_stones(captured)
        self.state.add_captures(opponent, len(captured))
        
        # Update Ko position (only if exactly one stone captured)
        if len(captured) == 1:
            self.state.ko_position = prev_hash
        else:
            self.state.ko_position = None
        
        # Record move and switch player
        move = Move(row, col, color)
        self.state.add_move(move)
        self.state.switch_player()
        
        if self.on_state_change:
            self.on_state_change()
        
        return True
    
    def pass_turn(self) -> None:
        """Pass the current turn."""
        if self.state.game_over:
            return
        
        color = self.state.current_player
        move = Move(0, 0, color, is_pass=True)
        self.state.add_move(move)
        self.state.switch_player()
        
        # Check for game end (two consecutive passes)
        if self.state.consecutive_passes >= 2:
            self._end_game()
        
        if self.on_state_change:
            self.on_state_change()
    
    def resign(self) -> None:
        """Current player resigns."""
        if self.state.game_over:
            return
        
        self.state.resigned = True
        self.state.winner = self.state.get_opponent(self.state.current_player)
        self.state.game_over = True
        
        if self.on_state_change:
            self.on_state_change()

    def _end_game(self) -> None:
        """End the game and determine winner."""
        self.state.game_over = True
        scores = self.calculate_score()
        
        if scores['black'] > scores['white']:
            self.state.winner = 'black'
        elif scores['white'] > scores['black']:
            self.state.winner = 'white'
        else:
            self.state.winner = 'tie'
    
    def get_current_player(self) -> str:
        """Get the current player's color."""
        return self.state.current_player
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.state.game_over
    
    def calculate_score(self) -> Dict[str, int]:
        """Calculate final scores using territory counting."""
        scores = {'black': 0, 'white': 0}
        
        # Count stones on board
        for row in range(self.board.size):
            for col in range(self.board.size):
                stone = self.board.get_stone(row, col)
                if stone:
                    scores[stone] += 1
        
        # Count territory (empty points surrounded by one color)
        visited = set()
        for row in range(self.board.size):
            for col in range(self.board.size):
                if (row, col) in visited:
                    continue
                if self.board.get_stone(row, col) is not None:
                    continue
                
                # Flood fill to find territory
                territory, borders = self._find_territory(row, col)
                visited.update(territory)
                
                # If bordered by only one color, it's that player's territory
                if len(borders) == 1:
                    color = list(borders)[0]
                    scores[color] += len(territory)
        
        # Add captured stones
        scores['black'] += self.state.captured_white
        scores['white'] += self.state.captured_black
        
        # Komi (compensation for white going second) - 6.5 points
        scores['white'] += 6.5
        
        return scores
    
    def _find_territory(self, start_row: int, start_col: int) -> Tuple[set, set]:
        """Find connected empty region and its bordering colors."""
        territory = set()
        borders = set()
        stack = [(start_row, start_col)]
        
        while stack:
            row, col = stack.pop()
            if (row, col) in territory:
                continue
            
            stone = self.board.get_stone(row, col)
            if stone is not None:
                borders.add(stone)
                continue
            
            territory.add((row, col))
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.board.size and 0 <= nc < self.board.size:
                    if (nr, nc) not in territory:
                        stack.append((nr, nc))
        
        return territory, borders
    
    def get_valid_moves(self) -> list:
        """Get all valid moves for current player."""
        valid = []
        color = self.state.current_player
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.is_valid_move(row, col, color, self.state.ko_position):
                    valid.append((row, col))
        return valid
    
    def get_last_move(self) -> Optional[Move]:
        """Get the last move made."""
        if self.state.move_history:
            return self.state.move_history[-1]
        return None
