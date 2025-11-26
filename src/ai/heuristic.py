"""Heuristic evaluator for Go game AI.

Heuristic Function Design:
H(board, color) = w1 × Territory + w2 × GroupStrength + w3 × Captures + w4 × Strategic

Justification:
- Territory (w1=1.0): Primary winning condition in Go
- GroupStrength (w2=1.5): Ensures AI builds strong, connected positions with many liberties
- Captures (w3=2.0): Weighted heavily as they directly reduce opponent's score
- Strategic (w4=0.8): Guides opening play toward valuable board areas (corners, edges)
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.board import Board


class HeuristicEvaluator:
    """Evaluates board positions for AI decision-making."""
    
    # Weight constants for heuristic components
    WEIGHT_TERRITORY = 1.0
    WEIGHT_GROUP_STRENGTH = 1.5
    WEIGHT_CAPTURES = 2.0
    WEIGHT_STRATEGIC = 0.8
    
    def __init__(self):
        """Initialize the heuristic evaluator."""
        # Strategic position values
        self.corner_positions = [(0, 0), (0, 8), (8, 0), (8, 8)]
        self.star_points = [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)]
        self.edge_positions = self._generate_edge_positions()
    
    def _generate_edge_positions(self) -> list:
        """Generate edge positions (excluding corners)."""
        edges = []
        for i in range(1, 8):
            edges.extend([(0, i), (8, i), (i, 0), (i, 8)])
        return edges
    
    def evaluate(self, board: 'Board', color: str, captured_by_color: int = 0, 
                 captured_by_opponent: int = 0) -> float:
        """
        Main evaluation function combining all heuristic components.
        Returns positive values for favorable positions, negative for unfavorable.
        """
        opponent = 'white' if color == 'black' else 'black'
        
        # Calculate each component
        territory = self.evaluate_territory(board, color)
        group_strength = self.evaluate_groups(board, color)
        captures = self.evaluate_captures(board, color, captured_by_color, captured_by_opponent)
        strategic = self.evaluate_strategic_positions(board, color)
        
        # Combine with weights
        score = (
            self.WEIGHT_TERRITORY * territory +
            self.WEIGHT_GROUP_STRENGTH * group_strength +
            self.WEIGHT_CAPTURES * captures +
            self.WEIGHT_STRATEGIC * strategic
        )
        
        return score

    def evaluate_territory(self, board: 'Board', color: str) -> float:
        """
        Evaluate territory control using influence mapping.
        Counts empty intersections closer to player's stones.
        """
        opponent = 'white' if color == 'black' else 'black'
        influence = [[0.0] * board.size for _ in range(board.size)]
        
        # Calculate influence from each stone
        for row in range(board.size):
            for col in range(board.size):
                stone = board.get_stone(row, col)
                if stone is None:
                    continue
                
                # Spread influence to nearby empty positions
                value = 1.0 if stone == color else -1.0
                for dr in range(-3, 4):
                    for dc in range(-3, 4):
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < board.size and 0 <= nc < board.size:
                            distance = abs(dr) + abs(dc)
                            if distance > 0:
                                influence[nr][nc] += value / distance
        
        # Count territory based on influence
        territory_score = 0.0
        for row in range(board.size):
            for col in range(board.size):
                if board.get_stone(row, col) is None:
                    if influence[row][col] > 0.5:
                        territory_score += 1.0
                    elif influence[row][col] < -0.5:
                        territory_score -= 1.0
        
        return territory_score
    
    def evaluate_groups(self, board: 'Board', color: str) -> float:
        """
        Evaluate group strength by analyzing liberties and connectivity.
        Score = sum of (liberties × group_size) for all groups.
        """
        opponent = 'white' if color == 'black' else 'black'
        
        player_score = 0.0
        opponent_score = 0.0
        
        # Evaluate player's groups
        for group in board.get_all_groups(color):
            liberties = len(board.get_group_liberties(group))
            group_size = len(group)
            player_score += liberties * group_size * 0.1
            
            # Bonus for groups with many liberties (safe groups)
            if liberties >= 4:
                player_score += group_size * 0.5
        
        # Evaluate opponent's groups
        for group in board.get_all_groups(opponent):
            liberties = len(board.get_group_liberties(group))
            group_size = len(group)
            opponent_score += liberties * group_size * 0.1
            
            if liberties >= 4:
                opponent_score += group_size * 0.5
        
        return player_score - opponent_score
    
    def evaluate_captures(self, board: 'Board', color: str, 
                         captured_by_color: int = 0, 
                         captured_by_opponent: int = 0) -> float:
        """
        Evaluate captures and potential captures.
        Considers actual captured stones and groups in atari (1 liberty).
        """
        opponent = 'white' if color == 'black' else 'black'
        
        # Actual captures difference
        capture_diff = captured_by_color - captured_by_opponent
        
        # Potential captures (opponent groups with 1 liberty - atari)
        potential_captures = 0
        for group in board.get_all_groups(opponent):
            liberties = len(board.get_group_liberties(group))
            if liberties == 1:
                potential_captures += len(group)
        
        # Threatened groups (our groups with 1 liberty)
        threatened = 0
        for group in board.get_all_groups(color):
            liberties = len(board.get_group_liberties(group))
            if liberties == 1:
                threatened += len(group)
        
        return capture_diff + potential_captures * 0.8 - threatened * 0.8
    
    def evaluate_strategic_positions(self, board: 'Board', color: str) -> float:
        """
        Evaluate strategic positioning (corners, edges, star points).
        Higher values for corners (3), edges (2), center (1).
        Only applies in early game (>60 empty positions).
        """
        empty_count = board.count_empty()
        
        # Reduce strategic weight as game progresses
        if empty_count < 30:
            return 0.0
        
        weight_modifier = min(1.0, empty_count / 60.0)
        
        opponent = 'white' if color == 'black' else 'black'
        score = 0.0
        
        # Corner positions (highest value)
        for pos in self.corner_positions:
            stone = board.get_stone(pos[0], pos[1])
            if stone == color:
                score += 3.0
            elif stone == opponent:
                score -= 3.0
        
        # Star points (good strategic positions)
        for pos in self.star_points:
            stone = board.get_stone(pos[0], pos[1])
            if stone == color:
                score += 2.0
            elif stone == opponent:
                score -= 2.0
        
        # Edge positions
        for pos in self.edge_positions:
            stone = board.get_stone(pos[0], pos[1])
            if stone == color:
                score += 1.0
            elif stone == opponent:
                score -= 1.0
        
        return score * weight_modifier
