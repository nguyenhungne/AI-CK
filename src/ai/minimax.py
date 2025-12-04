"""Minimax AI with alpha-beta pruning for Go game.

Depth Limit Strategy:
- Opening (>60 empty): depth=2 - High branching factor, focus on strategic positions
- Middle (30-60 empty): depth=3 - Balanced search, tactical opportunities emerge
- Endgame (<30 empty): depth=4 - Lower branching factor, deeper search feasible

This adaptive approach ensures AI responds within 5 seconds while maximizing search depth.
"""
import time
import logging
from typing import Tuple, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.board import Board

from src.ai.heuristic import HeuristicEvaluator

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class MinimaxAI:
    """Implements Heuristic Minimax Search with alpha-beta pruning."""
    
    TIMEOUT = 20.0  # Maximum time for move calculation in seconds
    MAX_CACHE_SIZE = 10000  # Maximum transposition table entries
    
    def __init__(self, depth_limit: Optional[int] = None):
        """
        Initialize Minimax AI.
        
        Args:
            depth_limit: Fixed depth limit, or None for adaptive depth
        """
        self.fixed_depth = depth_limit
        self.heuristic = HeuristicEvaluator()
        self.start_time = 0.0
        self.nodes_evaluated = 0
        self.captured_by_ai = 0
        self.captured_by_opponent = 0
        self.transposition_table = {}  # Cache for evaluated positions
        self.timeout_occurred = False  # Track if timeout happened
        self.cache_hits = 0  # Track cache hits
    
    def get_adaptive_depth(self, board: 'Board') -> int:
        """
        Determine search depth based on game phase.
        
        Returns:
            Depth limit based on number of empty positions
        """
        if self.fixed_depth is not None:
            return self.fixed_depth
        
        empty_count = board.count_empty()
        
        if empty_count > 60:
            return 1  # Opening: high branching factor
        elif empty_count > 30:
            return 2  # Middle game
        else:
            return 3  # Endgame: lower branching factor
    
    def find_best_move(self, board: 'Board', color: str, 
                       captured_by_ai: int = 0, 
                       captured_by_opponent: int = 0) -> Optional[Tuple[int, int]]:
        """
        Find the best move using minimax with alpha-beta pruning.
        
        Args:
            board: Current board state
            color: AI's color ('black' or 'white')
            captured_by_ai: Stones captured by AI
            captured_by_opponent: Stones captured by opponent
            
        Returns:
            Best move as (row, col) tuple, or None if no valid moves
        """
        self.start_time = time.time()
        self.nodes_evaluated = 0
        self.timeout_occurred = False
        self.cache_hits = 0
        self.captured_by_ai = captured_by_ai
        self.captured_by_opponent = captured_by_opponent
        
        # Clear transposition table if too large
        if len(self.transposition_table) > self.MAX_CACHE_SIZE:
            logger.debug(f"Clearing transposition table (size: {len(self.transposition_table)})")
            self.transposition_table.clear()
        
        depth = self.get_adaptive_depth(board)
        moves = self.get_possible_moves(board, color)
        empty_count = board.count_empty()
        
        logger.info(f"=== AI Turn ({color}) ===")
        logger.info(f"Empty positions: {empty_count}, Search depth: {depth}, Possible moves: {len(moves)}")
        
        if not moves:
            logger.warning("No valid moves available!")
            return None
        
        best_move = moves[0]
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        moves_evaluated = 0
        
        for move in moves:
            if self._is_timeout():
                self.timeout_occurred = True
                logger.warning(f"TIMEOUT after evaluating {moves_evaluated}/{len(moves)} moves!")
                break
            
            # Simulate move
            test_board = board.clone()
            test_board.place_stone(move[0], move[1], color)
            
            # Process captures
            opponent = 'white' if color == 'black' else 'black'
            captured = test_board.find_captured_stones(opponent)
            test_board.remove_stones(captured)
            
            # Evaluate with minimax
            score = self.minimax(
                test_board, depth - 1, alpha, beta, False, color,
                self.captured_by_ai + len(captured), self.captured_by_opponent
            )
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
            moves_evaluated += 1
        
        # Log results
        elapsed_time = time.time() - self.start_time
        logger.info(f"Best move: {best_move}, Score: {best_score:.2f}")
        logger.info(f"Time: {elapsed_time:.3f}s, Nodes: {self.nodes_evaluated}, Cache hits: {self.cache_hits}")
        
        if self.timeout_occurred:
            logger.warning(f"Search incomplete due to timeout ({self.TIMEOUT}s limit)")
        else:
            logger.info("Search completed successfully")
        
        logger.info(f"{'='*30}")
        
        return best_move

    def minimax(self, board: 'Board', depth: int, alpha: float, beta: float,
                maximizing: bool, ai_color: str,
                ai_captures: int, opponent_captures: int) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player's turn
            ai_color: AI's color
            ai_captures: Stones captured by AI
            opponent_captures: Stones captured by opponent
            
        Returns:
            Evaluation score for the position
        """
        self.nodes_evaluated += 1
        
        # Check transposition table
        board_key = (board.board_hash(), depth, maximizing, ai_captures, opponent_captures)
        if board_key in self.transposition_table:
            self.cache_hits += 1
            return self.transposition_table[board_key]
        
        # Terminal conditions
        if depth == 0 or self._is_timeout():
            score = self.heuristic.evaluate(
                board, ai_color, ai_captures, opponent_captures
            )
            self.transposition_table[board_key] = score
            return score
        
        current_color = ai_color if maximizing else ('white' if ai_color == 'black' else 'black')
        opponent_color = 'white' if current_color == 'black' else 'black'
        
        moves = self.get_possible_moves(board, current_color)
        
        if not moves:
            # No valid moves - evaluate current position
            return self.heuristic.evaluate(
                board, ai_color, ai_captures, opponent_captures
            )
        
        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                if self._is_timeout():
                    break
                
                test_board = board.clone()
                test_board.place_stone(move[0], move[1], current_color)
                
                captured = test_board.find_captured_stones(opponent_color)
                test_board.remove_stones(captured)
                
                new_ai_captures = ai_captures + len(captured)
                
                eval_score = self.minimax(
                    test_board, depth - 1, alpha, beta, False, ai_color,
                    new_ai_captures, opponent_captures
                )
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            self.transposition_table[board_key] = max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                if self._is_timeout():
                    break
                
                test_board = board.clone()
                test_board.place_stone(move[0], move[1], current_color)
                
                captured = test_board.find_captured_stones(opponent_color)
                test_board.remove_stones(captured)
                
                new_opponent_captures = opponent_captures + len(captured)
                
                eval_score = self.minimax(
                    test_board, depth - 1, alpha, beta, True, ai_color,
                    ai_captures, new_opponent_captures
                )
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            self.transposition_table[board_key] = min_eval
            return min_eval
    
    def get_possible_moves(self, board: 'Board', color: str) -> List[Tuple[int, int]]:
        """
        Generate possible moves, ordered by priority.
        After opening, limits moves to positions near existing stones.
        """
        empty_count = board.count_empty()
        all_empty = board.get_empty_positions()
        
        # In opening, consider all positions but prioritize strategic ones
        if empty_count > 70:
            return self._order_moves(board, all_empty, color)
        
        # After opening, focus on positions near existing stones
        near_stones = set()
        for row in range(board.size):
            for col in range(board.size):
                if board.get_stone(row, col) is not None:
                    # Add positions within 2 spaces
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = row + dr, col + dc
                            if (0 <= nr < board.size and 0 <= nc < board.size and
                                board.get_stone(nr, nc) is None):
                                near_stones.add((nr, nc))
        
        # Also include star points if empty
        star_points = [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)]
        for pos in star_points:
            if board.get_stone(pos[0], pos[1]) is None:
                near_stones.add(pos)
        
        moves = list(near_stones) if near_stones else all_empty
        return self._order_moves(board, moves, color)
    
    def _order_moves(self, board: 'Board', moves: List[Tuple[int, int]], 
                     color: str) -> List[Tuple[int, int]]:
        """Order moves by priority: captures, threats, strategic positions."""
        scored_moves = []
        opponent = 'white' if color == 'black' else 'black'
        
        for move in moves:
            if not board.is_valid_move(move[0], move[1], color):
                continue
            
            score = 0
            
            # Check if move captures opponent stones
            test_board = board.clone()
            test_board.place_stone(move[0], move[1], color)
            captured = test_board.find_captured_stones(opponent)
            score += len(captured) * 10
            
            # Strategic position bonus
            if move in [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)]:
                score += 3
            elif move[0] in [0, 8] or move[1] in [0, 8]:
                score += 1
            
            scored_moves.append((score, move))
        
        # Sort by score descending
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in scored_moves]
    
    def _is_timeout(self) -> bool:
        """Check if search has exceeded time limit."""
        return time.time() - self.start_time > self.TIMEOUT
