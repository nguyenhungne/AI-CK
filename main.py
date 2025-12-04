"""Main entry point for Go Game 9x9."""
import pygame
import threading
from src.controllers.game_controller import GameController
from src.ui.game_ui import GameUI
from src.players.human_player import HumanPlayer
from src.players.ai_player import AIPlayer


class GoGame:
    """Main game application class."""
    
    def __init__(self):
        """Initialize the game."""
        self.controller = GameController(mode='human_vs_human')
        self.ui = GameUI(self.controller)
        
        # Players
        self.black_player = HumanPlayer('black')
        self.white_player = HumanPlayer('white')
        
        # Human player color in AI mode (default: black)
        self.human_color = 'black'
        
        # AI computation state
        self.ai_thinking = False
        self.ai_move = None
        
        # Set up state change callback
        self.controller.on_state_change = self._on_state_change
        
        # Set up swap team callback
        self.ui.on_swap_team_callback = self._on_swap_team
    
    def _on_state_change(self) -> None:
        """Handle game state changes."""
        # Update AI player captures if in AI mode
        ai_player = self._get_ai_player()
        if ai_player:
            ai_player.update_captures(
                self.controller.state.captured_black,
                self.controller.state.captured_white
            )
    
    def _on_swap_team(self) -> None:
        """Handle swap team - switch human player color."""
        self.human_color = 'white' if self.human_color == 'black' else 'black'
        self.ui.human_color = self.human_color  # Sync with UI
        self._setup_players()
        self.controller.start_game()
        self.ai_move = None
        self.ai_thinking = False
    
    def _get_ai_player(self):
        """Get the AI player if exists."""
        if self.controller.mode == 'human_vs_ai':
            if isinstance(self.black_player, AIPlayer):
                return self.black_player
            if isinstance(self.white_player, AIPlayer):
                return self.white_player
        return None
    
    def _setup_players(self) -> None:
        """Set up players based on game mode."""
        if self.controller.mode == 'human_vs_ai':
            if self.human_color == 'black':
                self.black_player = HumanPlayer('black')
                self.white_player = AIPlayer('white')
            else:
                self.black_player = AIPlayer('black')
                self.white_player = HumanPlayer('white')
        else:
            self.black_player = HumanPlayer('black')
            self.white_player = HumanPlayer('white')
    
    def _get_current_player_obj(self):
        """Get the current player object."""
        if self.controller.get_current_player() == 'black':
            return self.black_player
        return self.white_player
    
    def _compute_ai_move(self) -> None:
        """Compute AI move in background thread."""
        ai_player = self._get_ai_player()
        if ai_player:
            self.ai_move = ai_player.get_move(self.controller.board)
        self.ai_thinking = False
    
    def _handle_ai_turn(self) -> None:
        """Handle AI player's turn."""
        if self.controller.is_game_over():
            return
        
        current = self.controller.get_current_player()
        ai_color = 'white' if self.human_color == 'black' else 'black'
        
        # Check if it's AI's turn
        if self.controller.mode == 'human_vs_ai' and current == ai_color:
            if not self.ai_thinking and self.ai_move is None:
                # Start AI computation in background
                self.ai_thinking = True
                thread = threading.Thread(target=self._compute_ai_move)
                thread.daemon = True
                thread.start()
            
            elif self.ai_move is not None:
                # Apply AI move
                if self.ai_move:
                    self.controller.make_move(self.ai_move[0], self.ai_move[1])
                else:
                    self.controller.pass_turn()
                self.ai_move = None
                
                if self.controller.is_game_over():
                    self.ui.show_game_over_overlay = True
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                # Check for mode change
                old_mode = self.controller.mode
                
                # Handle UI events
                click_pos = self.ui.handle_event(event)
                
                # Setup players if mode changed
                if self.controller.mode != old_mode:
                    self._setup_players()
                    self.ai_move = None
                    self.ai_thinking = False
                
                # Handle board click for human players
                if click_pos and not self.ai_thinking:
                    current = self.controller.get_current_player()
                    
                    # Only allow human moves
                    is_human_turn = (
                        self.controller.mode == 'human_vs_human' or
                        (self.controller.mode == 'human_vs_ai' and current == self.human_color)
                    )
                    
                    if is_human_turn:
                        row, col = click_pos
                        if self.controller.make_move(row, col):
                            if self.controller.is_game_over():
                                self.ui.show_game_over_overlay = True
            
            # Handle AI turn
            self._handle_ai_turn()
            
            # Draw
            self.ui.draw()
            self.ui.update()
        
        self.ui.quit()


def main():
    """Entry point."""
    game = GoGame()
    game.run()


if __name__ == '__main__':
    main()
