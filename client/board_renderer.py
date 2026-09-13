"""Board rendering for Monopoly GUI"""

import pygame
from typing import Dict, Tuple, List

# Colors for property groups
PROPERTY_COLORS = {
    'brown': (139, 69, 19),
    'light_blue': (173, 216, 230),
    'pink': (255, 192, 203),
    'orange': (255, 165, 0),
    'red': (255, 0, 0),
    'yellow': (255, 255, 0),
    'green': (0, 128, 0),
    'dark_blue': (0, 0, 139),
    'railroad': (128, 128, 128),
    'utility': (192, 192, 192),
    'special': (200, 200, 200),
}

PLAYER_COLORS = [
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
]


class BoardRenderer:
    """Renders the Monopoly board"""
    
    def __init__(self, board_properties: List[Dict]):
        self.properties = board_properties
        self.board_size = 40
        
        # Board dimensions
        self.cell_size = 80
        self.corner_size = 100
        self.center_spacing = 150
        
        # Calculate board dimensions
        self.board_width = self.corner_size * 2 + self.cell_size * 9
        self.board_height = self.board_width
        self.board_x = 50
        self.board_y = 50
    
    def get_cell_position(self, position: int) -> Tuple[int, int, int, int]:
        """Get the rect for a property on the board"""
        if position == 0:  # GO
            return (self.board_x + self.board_width - self.corner_size,
                    self.board_y + self.board_height - self.corner_size,
                    self.corner_size, self.corner_size)
        
        elif 1 <= position <= 9:  # Bottom side (right to left)
            x = self.board_x + self.board_width - self.corner_size - (position * self.cell_size)
            y = self.board_y + self.board_height - self.corner_size
            return (x, y, self.cell_size, self.corner_size)
        
        elif position == 10:  # JAIL
            return (self.board_x, self.board_y + self.board_height - self.corner_size,
                    self.corner_size, self.corner_size)
        
        elif 11 <= position <= 19:  # Left side (bottom to top)
            x = self.board_x
            y = self.board_y + self.board_height - self.corner_size - ((position - 10) * self.cell_size)
            return (x, y, self.corner_size, self.cell_size)
        
        elif position == 20:  # Free Parking
            return (self.board_x, self.board_y,
                    self.corner_size, self.corner_size)
        
        elif 21 <= position <= 29:  # Top side (left to right)
            x = self.board_x + self.corner_size + ((position - 20) * self.cell_size)
            y = self.board_y
            return (x, y, self.cell_size, self.corner_size)
        
        elif position == 30:  # GO TO JAIL
            return (self.board_x + self.board_width - self.corner_size, self.board_y,
                    self.corner_size, self.corner_size)
        
        elif 31 <= position <= 39:  # Right side (top to bottom)
            x = self.board_x + self.board_width - self.corner_size
            y = self.board_y + self.corner_size + ((position - 30) * self.cell_size)
            return (x, y, self.corner_size, self.cell_size)
        
        return (0, 0, 0, 0)
    
    def draw_board(self, screen: pygame.Surface):
        """Draw the Monopoly board"""
        # Draw outer border
        border_rect = pygame.Rect(self.board_x, self.board_y, self.board_width, self.board_height)
        pygame.draw.rect(screen, (0, 0, 0), border_rect, 3)
        
        # Draw center area
        center_x = self.board_x + self.board_width // 2
        center_y = self.board_y + self.board_height // 2
        pygame.draw.rect(screen, (240, 240, 240),
                        pygame.Rect(center_x - self.center_spacing // 2,
                                  center_y - self.center_spacing // 2,
                                  self.center_spacing,
                                  self.center_spacing))
        
        # Draw "Free Parking" text in center
        font = pygame.font.Font(None, 24)
        center_text = font.render("FREE PARKING", True, (0, 0, 0))
        screen.blit(center_text, (center_x - 60, center_y - 10))
        
        # Draw each property
        for i, prop in enumerate(self.properties):
            self.draw_property(screen, i, prop)
    
    def draw_property(self, screen: pygame.Surface, position: int, prop: Dict):
        """Draw a single property"""
        x, y, width, height = self.get_cell_position(position)
        
        # Get property color
        color = PROPERTY_COLORS.get(prop.get('color', 'special'), (200, 200, 200))
        
        # Draw background
        pygame.draw.rect(screen, color, (x, y, width, height))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 1)
        
        # Draw property info
        font_small = pygame.font.Font(None, 16)
        name_text = font_small.render(prop.get('name', '')[:15], True, (0, 0, 0))
        
        # Position text based on board position
        if position in [0, 10, 20, 30]:  # Corners
            text_x = x + 5
            text_y = y + 5
        elif position in range(1, 10):  # Bottom
            text_x = x + 5
            text_y = y + 30
        elif position in range(11, 20):  # Left
            text_x = x + 5
            text_y = y + height // 2
        elif position in range(21, 30):  # Top
            text_x = x + 5
            text_y = y + 5
        else:  # Right
            text_x = x + 5
            text_y = y + height // 2
        
        screen.blit(name_text, (text_x, text_y))
        
        # Draw price if applicable
        if prop.get('price', 0) > 0:
            price_text = font_small.render(f"${prop.get('price')}", True, (0, 0, 0))
            if position in range(1, 10) or position in range(21, 30):
                screen.blit(price_text, (text_x, text_y + 20))
            else:
                screen.blit(price_text, (text_x, text_y + 15))
    
    def draw_players(self, screen: pygame.Surface, players: List[Dict]):
        """Draw player tokens on the board"""
        for idx, player in enumerate(players):
            position = player.get('position', 0)
            x, y, width, height = self.get_cell_position(position)
            
            # Calculate token position (multiple players on same property)
            offset = (idx % 2) * 20
            token_x = x + 10 + offset
            token_y = y + 10 + offset
            
            # Draw player token
            color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
            pygame.draw.circle(screen, color, (token_x, token_y), 8)
            pygame.draw.circle(screen, (0, 0, 0), (token_x, token_y), 8, 2)
            
            # Draw player initial
            font = pygame.font.Font(None, 12)
            initial = player.get('name', 'P')[0].upper()
            initial_text = font.render(initial, True, (255, 255, 255))
            screen.blit(initial_text, (token_x - 3, token_y - 5))


class InfoPanel:
    """Shows game info on the side"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen: pygame.Surface, game_state: Dict):
        """Draw info panel"""
        # Draw background
        pygame.draw.rect(screen, (240, 240, 240), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        font_title = pygame.font.Font(None, 24)
        font_normal = pygame.font.Font(None, 20)
        
        y_offset = self.rect.y + 10
        
        # Current player
        current_player = game_state.get('current_player', 'Unknown')
        title = font_title.render(f"Current: {current_player}", True, (0, 0, 0))
        screen.blit(title, (self.rect.x + 10, y_offset))
        
        y_offset += 40
        
        # Players info
        for idx, player in enumerate(game_state.get('players', [])):
            name = player.get('name', 'Unknown')
            money = player.get('money', 0)
            position = player.get('position', 0)
            
            color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
            
            # Draw player color indicator
            pygame.draw.circle(screen, color, (self.rect.x + 15, y_offset + 5), 5)
            
            # Draw player info
            info_text = f"{name}: ${money} (Pos {position})"
            text = font_normal.render(info_text, True, (0, 0, 0))
            screen.blit(text, (self.rect.x + 30, y_offset))
            
            y_offset += 30
