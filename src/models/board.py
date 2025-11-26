"""Board class for Go game - manages board state and game rules."""
from typing import List, Tuple, Optional, Set
import copy


class Board:
    """Represents a Go game board with stone placement and rule enforcement."""
    
    def __init__(self, size: int = 9):
        """Initialize an empty board."""
        self.size = size
        self.grid: List[List[Optional[str]]] = [[None] * size for _ in range(size)]
        self.previous_hash: Optional[int] = None
    
    def get_stone(self, row: int, col: int) -> Optional[str]:
        """Get the stone at a position, or None if empty."""
        if not self._is_on_board(row, col):
            return None
        return self.grid[row][col]
    
    def place_stone(self, row: int, col: int, color: str) -> bool:
        """Place a stone on the board. Returns True if successful."""
        if not self._is_on_board(row, col):
            return False
        if self.grid[row][col] is not None:
            return False
        self.grid[row][col] = color
        return True
    
    def remove_stone(self, row: int, col: int) -> None:
        """Remove a stone from the board."""
        if self._is_on_board(row, col):
            self.grid[row][col] = None
    
    def remove_stones(self, positions: List[Tuple[int, int]]) -> None:
        """Remove multiple stones from the board."""
        for row, col in positions:
            self.remove_stone(row, col)
    
    def _is_on_board(self, row: int, col: int) -> bool:
        """Check if position is within board bounds."""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def _get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get adjacent positions (up, down, left, right)."""
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self._is_on_board(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def get_group(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """Find all connected stones of the same color using flood-fill."""
        color = self.get_stone(row, col)
        if color is None:
            return set()
        
        group = set()
        stack = [(row, col)]
        
        while stack:
            r, c = stack.pop()
            if (r, c) in group:
                continue
            if self.get_stone(r, c) != color:
                continue
            group.add((r, c))
            for nr, nc in self._get_neighbors(r, c):
                if (nr, nc) not in group:
                    stack.append((nr, nc))
        
        return group
    
    def get_liberties(self, row: int, col: int) -> int:
        """Count liberties for the group containing the stone at position."""
        group = self.get_group(row, col)
        if not group:
            return 0
        
        liberties = set()
        for r, c in group:
            for nr, nc in self._get_neighbors(r, c):
                if self.get_stone(nr, nc) is None:
                    liberties.add((nr, nc))
        
        return len(liberties)
    
    def get_group_liberties(self, group: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Get all liberty positions for a group."""
        liberties = set()
        for r, c in group:
            for nr, nc in self._get_neighbors(r, c):
                if self.get_stone(nr, nc) is None:
                    liberties.add((nr, nc))
        return liberties
    
    def find_captured_stones(self, opponent_color: str) -> List[Tuple[int, int]]:
        """Find all opponent stones that have been captured (zero liberties)."""
        captured = []
        visited = set()
        
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in visited:
                    continue
                if self.get_stone(row, col) != opponent_color:
                    continue
                
                group = self.get_group(row, col)
                visited.update(group)
                
                if self.get_liberties(row, col) == 0:
                    captured.extend(group)
        
        return captured
    
    def is_valid_move(self, row: int, col: int, color: str, ko_hash: Optional[int] = None) -> bool:
        """Check if a move is valid (empty, not self-capture, not Ko)."""
        if not self._is_on_board(row, col):
            return False
        if self.grid[row][col] is not None:
            return False
        
        # Simulate the move
        test_board = self.clone()
        test_board.place_stone(row, col, color)
        
        # Check for captures first
        opponent = 'white' if color == 'black' else 'black'
        captured = test_board.find_captured_stones(opponent)
        test_board.remove_stones(captured)
        
        # Check for self-capture
        if test_board.get_liberties(row, col) == 0:
            return False
        
        # Check Ko rule
        if ko_hash is not None and test_board.board_hash() == ko_hash:
            return False
        
        return True
    
    def board_hash(self) -> int:
        """Generate a hash of the current board state for Ko detection."""
        return hash(tuple(tuple(row) for row in self.grid))
    
    def clone(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board(self.size)
        new_board.grid = copy.deepcopy(self.grid)
        new_board.previous_hash = self.previous_hash
        return new_board
    
    def get_empty_positions(self) -> List[Tuple[int, int]]:
        """Get all empty positions on the board."""
        empty = []
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] is None:
                    empty.append((row, col))
        return empty
    
    def count_empty(self) -> int:
        """Count empty positions on the board."""
        return len(self.get_empty_positions())
    
    def get_all_groups(self, color: str) -> List[Set[Tuple[int, int]]]:
        """Get all groups of a specific color."""
        groups = []
        visited = set()
        
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in visited:
                    continue
                if self.get_stone(row, col) != color:
                    continue
                
                group = self.get_group(row, col)
                visited.update(group)
                groups.append(group)
        
        return groups
