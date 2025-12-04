"""Game UI using Pygame for Go game."""
import pygame
from typing import Optional, Tuple, TYPE_CHECKING
from src.ui.button import Button

if TYPE_CHECKING:
    from src.controllers.game_controller import GameController


# Colors
BOARD_COLOR = (220, 179, 92)
LINE_COLOR = (50, 40, 30)
BLACK_STONE = (20, 20, 20)
WHITE_STONE = (240, 240, 240)
SHADOW_COLOR = (100, 80, 60, 100)
HOVER_COLOR = (100, 100, 100, 128)
INFO_BG = (60, 60, 70)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 200, 0)


class GameUI:
    """Pygame-based user interface for Go game."""
    
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    BOARD_SIZE = 540
    BOARD_OFFSET_X = 30
    BOARD_OFFSET_Y = 30
    INFO_PANEL_X = 600
    
    def __init__(self, controller: 'GameController'):
        """Initialize the game UI."""
        self.controller = controller
        
        pygame.init()
        pygame.display.set_caption("Go Game 9x9")
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        
        # Calculate grid spacing
        self.grid_size = self.BOARD_SIZE // 10
        self.stone_radius = self.grid_size // 2 - 2
        
        # Star points (handicap positions)
        self.star_points = [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)]
        
        # Hover position
        self.hover_pos: Optional[Tuple[int, int]] = None
        
        # Game over state
        self.show_game_over_overlay = False
        
        # Buttons
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create UI buttons."""
        btn_x = self.INFO_PANEL_X + 20
        btn_width = 160
        btn_height = 35
        
        self.btn_new_game = Button(
            btn_x, 200, btn_width, btn_height, "New Game",
            callback=self._on_new_game,
            color=(70, 130, 70), hover_color=(90, 160, 90)
        )
        
        self.btn_pass = Button(
            btn_x, 250, btn_width, btn_height, "Pass",
            callback=self._on_pass,
            color=(100, 100, 140), hover_color=(120, 120, 170)
        )
        
        self.btn_resign = Button(
            btn_x, 300, btn_width, btn_height, "Resign",
            callback=self._on_resign,
            color=(140, 70, 70), hover_color=(170, 90, 90)
        )
        
        self.btn_vs_human = Button(
            btn_x, 400, btn_width, btn_height, "vs Human",
            callback=lambda: self._set_mode('human_vs_human'),
            color=(80, 80, 120), hover_color=(100, 100, 150)
        )
        
        self.btn_vs_ai = Button(
            btn_x, 450, btn_width, btn_height, "vs AI",
            callback=lambda: self._set_mode('human_vs_ai'),
            color=(80, 80, 120), hover_color=(100, 100, 150)
        )
        
        self.btn_swap_team = Button(
            btn_x, 500, btn_width, btn_height, "Swap Team",
            callback=self._on_swap_team,
            color=(120, 100, 80), hover_color=(150, 130, 100)
        )
        
        self.buttons = [
            self.btn_new_game, self.btn_pass, self.btn_resign,
            self.btn_vs_human, self.btn_vs_ai, self.btn_swap_team
        ]
        
        # Callback for swap team (to be set by main)
        self.on_swap_team_callback = None
        
        # Human player color (to be set by main)
        self.human_color = 'black'

    def _on_new_game(self) -> None:
        """Handle new game button click."""
        self.controller.start_game()
        self.show_game_over_overlay = False
    
    def _on_pass(self) -> None:
        """Handle pass button click."""
        self.controller.pass_turn()
        if self.controller.is_game_over():
            self.show_game_over_overlay = True
    
    def _on_resign(self) -> None:
        """Handle resign button click."""
        self.controller.resign()
        self.show_game_over_overlay = True
    
    def _set_mode(self, mode: str) -> None:
        """Set game mode and restart."""
        self.controller.mode = mode
        self.controller.start_game()
        self.show_game_over_overlay = False
    
    def _on_swap_team(self) -> None:
        """Handle swap team button click."""
        if self.on_swap_team_callback:
            self.on_swap_team_callback()
            # Don't call start_game here - callback handles it
        self.show_game_over_overlay = False
    
    def _board_to_pixel(self, row: int, col: int) -> Tuple[int, int]:
        """Convert board coordinates to pixel coordinates."""
        x = self.BOARD_OFFSET_X + self.grid_size + col * self.grid_size
        y = self.BOARD_OFFSET_Y + self.grid_size + row * self.grid_size
        return x, y
    
    def _pixel_to_board(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Convert pixel coordinates to board coordinates."""
        col = round((x - self.BOARD_OFFSET_X - self.grid_size) / self.grid_size)
        row = round((y - self.BOARD_OFFSET_Y - self.grid_size) / self.grid_size)
        
        if 0 <= row < 9 and 0 <= col < 9:
            # Check if click is close enough to intersection
            px, py = self._board_to_pixel(row, col)
            if abs(x - px) < self.grid_size // 2 and abs(y - py) < self.grid_size // 2:
                return row, col
        return None
    
    def draw(self) -> None:
        """Draw the complete game interface."""
        self.screen.fill(INFO_BG)
        
        # Draw board
        self._draw_board()
        
        # Draw stones
        self._draw_stones()
        
        # Draw hover preview
        self._draw_hover()
        
        # Draw last move indicator
        self._draw_last_move()
        
        # Draw info panel
        self._draw_info_panel()
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw game over overlay
        if self.show_game_over_overlay:
            self._draw_game_over()
        
        pygame.display.flip()
    
    def _draw_board(self) -> None:
        """Draw the game board with grid lines."""
        # Board background
        board_rect = pygame.Rect(
            self.BOARD_OFFSET_X, self.BOARD_OFFSET_Y,
            self.BOARD_SIZE, self.BOARD_SIZE
        )
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect)
        
        # Grid lines
        for i in range(9):
            # Vertical lines
            x = self.BOARD_OFFSET_X + self.grid_size + i * self.grid_size
            y1 = self.BOARD_OFFSET_Y + self.grid_size
            y2 = self.BOARD_OFFSET_Y + self.grid_size * 9
            pygame.draw.line(self.screen, LINE_COLOR, (x, y1), (x, y2), 1)
            
            # Horizontal lines
            y = self.BOARD_OFFSET_Y + self.grid_size + i * self.grid_size
            x1 = self.BOARD_OFFSET_X + self.grid_size
            x2 = self.BOARD_OFFSET_X + self.grid_size * 9
            pygame.draw.line(self.screen, LINE_COLOR, (x1, y), (x2, y), 1)
        
        # Star points
        for row, col in self.star_points:
            x, y = self._board_to_pixel(row, col)
            pygame.draw.circle(self.screen, LINE_COLOR, (x, y), 4)
    
    def _draw_stones(self) -> None:
        """Draw all stones on the board."""
        for row in range(9):
            for col in range(9):
                stone = self.controller.board.get_stone(row, col)
                if stone:
                    self._draw_stone(row, col, stone)
    
    def _draw_stone(self, row: int, col: int, color: str) -> None:
        """Draw a single stone with shadow."""
        x, y = self._board_to_pixel(row, col)
        
        # Shadow
        shadow_surface = pygame.Surface((self.stone_radius * 2 + 4, self.stone_radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 60), 
                          (self.stone_radius + 2, self.stone_radius + 2), self.stone_radius)
        self.screen.blit(shadow_surface, (x - self.stone_radius, y - self.stone_radius + 2))
        
        # Stone
        stone_color = BLACK_STONE if color == 'black' else WHITE_STONE
        pygame.draw.circle(self.screen, stone_color, (x, y), self.stone_radius)
        
        # Highlight for white stones
        if color == 'white':
            pygame.draw.circle(self.screen, (200, 200, 200), (x - 5, y - 5), 5)

    def _draw_hover(self) -> None:
        """Draw hover preview for valid moves."""
        if self.hover_pos and not self.controller.is_game_over():
            row, col = self.hover_pos
            color = self.controller.get_current_player()
            
            if self.controller.board.is_valid_move(row, col, color, 
                                                    self.controller.state.ko_position):
                x, y = self._board_to_pixel(row, col)
                
                # Semi-transparent preview
                preview_surface = pygame.Surface((self.stone_radius * 2, self.stone_radius * 2), pygame.SRCALPHA)
                stone_color = (20, 20, 20, 128) if color == 'black' else (240, 240, 240, 128)
                pygame.draw.circle(preview_surface, stone_color, 
                                  (self.stone_radius, self.stone_radius), self.stone_radius)
                self.screen.blit(preview_surface, (x - self.stone_radius, y - self.stone_radius))
    
    def _draw_last_move(self) -> None:
        """Draw indicator on the last played stone."""
        last_move = self.controller.get_last_move()
        if last_move and not last_move.is_pass:
            x, y = self._board_to_pixel(last_move.row, last_move.col)
            
            # Draw small circle marker
            marker_color = WHITE_STONE if last_move.color == 'black' else BLACK_STONE
            pygame.draw.circle(self.screen, marker_color, (x, y), 5)
    
    def _draw_info_panel(self) -> None:
        """Draw the information panel."""
        # Panel background
        panel_rect = pygame.Rect(self.INFO_PANEL_X, 0, 200, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, INFO_BG, panel_rect)
        
        # Title
        title = self.font.render("Go Game 9x9", True, TEXT_COLOR)
        self.screen.blit(title, (self.INFO_PANEL_X + 40, 20))
        
        # Current player
        current = self.controller.get_current_player()
        turn_text = self.font.render(f"Turn: {current.capitalize()}", True, TEXT_COLOR)
        self.screen.blit(turn_text, (self.INFO_PANEL_X + 20, 60))
        
        # Turn indicator circle
        indicator_color = BLACK_STONE if current == 'black' else WHITE_STONE
        pygame.draw.circle(self.screen, indicator_color, (self.INFO_PANEL_X + 160, 68), 12)
        pygame.draw.circle(self.screen, (100, 100, 100), (self.INFO_PANEL_X + 160, 68), 12, 1)
        
        # Captured stones
        captured_title = self.small_font.render("Captured:", True, TEXT_COLOR)
        self.screen.blit(captured_title, (self.INFO_PANEL_X + 20, 100))
        
        black_cap = self.small_font.render(f"Black: {self.controller.state.captured_white}", True, TEXT_COLOR)
        white_cap = self.small_font.render(f"White: {self.controller.state.captured_black}", True, TEXT_COLOR)
        self.screen.blit(black_cap, (self.INFO_PANEL_X + 20, 125))
        self.screen.blit(white_cap, (self.INFO_PANEL_X + 20, 150))
        
        # Mode indicator
        mode_text = "Human vs Human" if self.controller.mode == 'human_vs_human' else "Human vs AI"
        mode_label = self.small_font.render(f"Mode: {mode_text}", True, (180, 180, 180))
        self.screen.blit(mode_label, (self.INFO_PANEL_X + 20, 350))
        
        # Your team indicator (only in AI mode)
        if self.controller.mode == 'human_vs_ai':
            team_text = f"You: {self.human_color.capitalize()}"
            team_label = self.small_font.render(team_text, True, (180, 180, 180))
            self.screen.blit(team_label, (self.INFO_PANEL_X + 20, 375))
        
        # Move count
        move_count = len(self.controller.state.move_history)
        moves_text = self.small_font.render(f"Moves: {move_count}", True, (180, 180, 180))
        self.screen.blit(moves_text, (self.INFO_PANEL_X + 20, 550))
    
    def _draw_game_over(self) -> None:
        """Draw game over overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game over box
        box_rect = pygame.Rect(200, 180, 400, 240)
        pygame.draw.rect(self.screen, (50, 50, 60), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), box_rect, 3, border_radius=10)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Game Over", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(400, 220))
        self.screen.blit(title, title_rect)
        
        # Winner
        if self.controller.state.resigned:
            winner_text = f"{self.controller.state.winner.capitalize()} wins by resignation!"
        elif self.controller.state.winner == 'tie':
            winner_text = "It's a tie!"
        else:
            winner_text = f"{self.controller.state.winner.capitalize()} wins!"
        
        winner = self.font.render(winner_text, True, HIGHLIGHT_COLOR)
        winner_rect = winner.get_rect(center=(400, 270))
        self.screen.blit(winner, winner_rect)
        
        # Scores
        scores = self.controller.calculate_score()
        score_text = f"Black: {scores['black']:.1f}  |  White: {scores['white']:.1f}"
        score = self.font.render(score_text, True, TEXT_COLOR)
        score_rect = score.get_rect(center=(400, 310))
        self.screen.blit(score, score_rect)
        
        # New game button on overlay
        new_game_btn = Button(300, 350, 200, 40, "New Game", 
                             callback=self._on_new_game,
                             color=(70, 130, 70), hover_color=(90, 160, 90))
        new_game_btn.draw(self.screen)
        self.overlay_button = new_game_btn
    
    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[int, int]]:
        """
        Handle pygame event.
        
        Returns:
            Board position if valid click, None otherwise
        """
        # Handle overlay button if game over
        if self.show_game_over_overlay and hasattr(self, 'overlay_button'):
            self.overlay_button.handle_event(event)
        
        # Handle regular buttons
        for button in self.buttons:
            button.handle_event(event)
        
        # Handle board interaction
        if event.type == pygame.MOUSEMOTION:
            pos = self._pixel_to_board(event.pos[0], event.pos[1])
            self.hover_pos = pos
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.show_game_over_overlay:
                pos = self._pixel_to_board(event.pos[0], event.pos[1])
                if pos:
                    return pos
        
        return None
    
    def update(self) -> None:
        """Update display and maintain frame rate."""
        self.clock.tick(60)
    
    def quit(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()
