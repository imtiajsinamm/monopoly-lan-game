"""Pygame GUI client for Monopoly LAN game"""

import pygame
import socketio
import json
from enum import Enum
from typing import Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)
COLOR_BLUE = (0, 0, 200)
COLOR_YELLOW = (255, 255, 0)
COLOR_GOLD = (255, 215, 0)


class GameState(Enum):
    """Game state enum"""
    MAIN_MENU = 1
    ROOM_SELECT = 2
    LOBBY = 3
    GAME = 4
    GAME_OVER = 5


class Button:
    """Simple button class"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
    
    def draw(self, screen):
        """Draw button"""
        color = COLOR_YELLOW if self.hovered else COLOR_GOLD
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 2)
        
        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, COLOR_BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        """Check if mouse is hovering"""
        self.hovered = self.rect.collidepoint(pos)
    
    def check_click(self, pos):
        """Check if button clicked"""
        if self.rect.collidepoint(pos) and self.callback:
            self.callback()


class TextInput:
    """Simple text input box"""
    
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
    
    def draw(self, screen):
        """Draw text input"""
        color = COLOR_BLUE if self.active else COLOR_LIGHT_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 2)
        
        font = pygame.font.Font(None, 24)
        display_text = self.text if self.text else self.placeholder
        text_surf = font.render(display_text, True, COLOR_BLACK if self.text else COLOR_LIGHT_GRAY)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
    
    def handle_event(self, event):
        """Handle keyboard events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    
    def get_value(self) -> str:
        """Get input value"""
        return self.text


class MonopolyGUIClient:
    """Pygame GUI client for Monopoly"""
    
    def __init__(self, server_url: str = "http://localhost:5555"):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Monopoly LAN Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        
        # Socket.IO client
        self.sio = socketio.Client()
        self.server_url = server_url
        self.player_name = ""
        self.room_code = ""
        self.game_state = None
        self.sid = None
        
        # UI Elements
        self.setup_ui()
        
        # Setup socket events
        self.setup_socket_events()
    
    def setup_ui(self):
        """Setup UI elements"""
        self.buttons = {}
        self.text_inputs = {}
    
    def setup_socket_events(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.on('connection_response')
        def on_connect(data):
            print(f"Connected to server: {data}")
            self.sid = data.get('sid')
        
        @self.sio.on('room_created')
        def on_room_created(data):
            print(f"Room created: {data}")
            self.room_code = data.get('room_code')
            self.state = GameState.LOBBY
        
        @self.sio.on('join_room_error')
        def on_join_error(data):
            print(f"Join error: {data}")
        
        @self.sio.on('player_joined')
        def on_player_joined(data):
            print(f"Player joined: {data}")
        
        @self.sio.on('game_started')
        def on_game_started(data):
            print(f"Game started!")
            self.game_state = data.get('game_state')
            self.state = GameState.GAME
        
        @self.sio.on('game_state_update')
        def on_game_state_update(data):
            self.game_state = data.get('game_state')
    
    def connect_to_server(self) -> bool:
        """Connect to the server"""
        try:
            self.sio.connect(self.server_url, wait_timeout=10)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def draw_main_menu(self):
        """Draw main menu screen"""
        self.screen.fill(COLOR_DARK_GRAY)
        
        # Title
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("MONOPOLY", True, COLOR_GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        font_small = pygame.font.Font(None, 48)
        subtitle = font_small.render("LAN Game", True, COLOR_YELLOW)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Player name input
        font_normal = pygame.font.Font(None, 28)
        name_label = font_normal.render("Enter your name:", True, COLOR_WHITE)
        self.screen.blit(name_label, (SCREEN_WIDTH // 2 - 150, 300))
        
        # Name input box
        if 'name_input' not in self.text_inputs:
            self.text_inputs['name_input'] = TextInput(SCREEN_WIDTH // 2 - 150, 350, 300, 40, "Your Name")
        
        self.text_inputs['name_input'].draw(self.screen)
        
        # Buttons
        button_y = 450
        
        if 'create_room' not in self.buttons:
            self.buttons['create_room'] = Button(
                SCREEN_WIDTH // 2 - 200, button_y, 180, 50,
                "Create Room",
                self.on_create_room
            )
        
        if 'join_room' not in self.buttons:
            self.buttons['join_room'] = Button(
                SCREEN_WIDTH // 2 + 20, button_y, 180, 50,
                "Join Room",
                self.on_join_room
            )
        
        for button in self.buttons.values():
            button.draw(self.screen)
    
    def draw_lobby(self):
        """Draw lobby screen"""
        self.screen.fill(COLOR_DARK_GRAY)
        
        font_large = pygame.font.Font(None, 48)
        title = font_large.render(f"Room: {self.room_code}", True, COLOR_GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Info
        font_normal = pygame.font.Font(None, 28)
        info = font_normal.render(f"Player: {self.player_name}", True, COLOR_WHITE)
        self.screen.blit(info, (50, 150))
        
        share = font_normal.render(f"Share code with others to join!", True, COLOR_YELLOW)
        self.screen.blit(share, (50, 200))
        
        # Buttons
        if 'ready_button' not in self.buttons:
            self.buttons['ready_button'] = Button(
                SCREEN_WIDTH // 2 - 100, 400, 200, 50,
                "I'm Ready!",
                self.on_ready
            )
        
        if 'start_button' not in self.buttons:
            self.buttons['start_button'] = Button(
                SCREEN_WIDTH // 2 - 100, 500, 200, 50,
                "Start Game",
                self.on_start_game
            )
        
        for button in self.buttons.values():
            button.draw(self.screen)
    
    def draw_game(self):
        """Draw game screen"""
        self.screen.fill(COLOR_DARK_GRAY)
        
        if not self.game_state:
            return
        
        font_large = pygame.font.Font(None, 48)
        current_player = font_large.render(
            f"Current: {self.game_state.get('current_player', 'Unknown')}",
            True, COLOR_GOLD
        )
        self.screen.blit(current_player, (50, 50))
        
        # Draw players info
        font_small = pygame.font.Font(None, 24)
        y_offset = 150
        for player in self.game_state.get('players', []):
            player_info = f"{player['name']}: ${player['money']} - Pos: {player['position']}"
            text = font_small.render(player_info, True, COLOR_WHITE)
            self.screen.blit(text, (50, y_offset))
            y_offset += 30
    
    def on_create_room(self):
        """Create room callback"""
        self.player_name = self.text_inputs['name_input'].get_value()
        if not self.player_name:
            print("Please enter a name")
            return
        
        self.sio.emit('create_room', {'player_name': self.player_name})
    
    def on_join_room(self):
        """Join room callback"""
        print("TODO: Implement join room")
        self.state = GameState.ROOM_SELECT
    
    def on_ready(self):
        """Ready callback"""
        self.sio.emit('set_ready', {
            'room_code': self.room_code,
            'player_name': self.player_name,
            'ready': True
        })
    
    def on_start_game(self):
        """Start game callback"""
        self.sio.emit('start_game', {
            'room_code': self.room_code,
            'player_name': self.player_name
        })
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle mouse hover
            if event.type == pygame.MOUSEMOTION:
                for button in self.buttons.values():
                    button.check_hover(event.pos)
            
            # Handle mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons.values():
                    button.check_click(event.pos)
            
            # Handle text input
            for text_input in self.text_inputs.values():
                text_input.handle_event(event)
    
    def update(self):
        """Update game state"""
        pass
    
    def draw(self):
        """Draw current screen"""
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.LOBBY:
            self.draw_lobby()
        elif self.state == GameState.GAME:
            self.draw_game()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        if not self.connect_to_server():
            print("Failed to connect to server")
            return
        
        print("Connected to server. Starting GUI...")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        self.sio.disconnect()


def main():
    """Main entry point"""
    client = MonopolyGUIClient(server_url="http://localhost:5555")
    client.run()


if __name__ == "__main__":
    main()
