"""Button class for Pygame UI elements."""
import pygame
from typing import Tuple, Callable, Optional


class Button:
    """Clickable button for Pygame interface."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Optional[Callable] = None,
                 color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (130, 130, 130),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize button.
        
        Args:
            x, y: Position
            width, height: Size
            text: Button label
            callback: Function to call on click
            color: Normal background color
            hover_color: Background color on hover
            text_color: Text color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the surface."""
        if self.font is None:
            self.font = pygame.font.Font(None, 24)
        
        # Draw background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2, border_radius=5)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.
        
        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        
        return False
    
    def set_text(self, text: str) -> None:
        """Update button text."""
        self.text = text
