"""Game server for Monopoly LAN game"""

import socket
import json
import threading
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game import Game


class GameServer:
    """Server that manages the Monopoly game over network"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        
        self.players: Dict[str, tuple] = {}  # player_name -> (address, port)
        self.game: Game = None
        self.game_started = False
        self.lock = threading.Lock()
    
    def start(self):
        """Start the server and listen for connections"""
        print(f"\n{'='*50}")
        print(f"Monopoly LAN Game Server")
        print(f"{'='*50}")
        print(f"Server started on {self.host}:{self.port}")
        print(f"Waiting for players to connect...")
        print(f"{'='*50}\n")
        
        while True:
            try:
                data, addr = self.server_socket.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                
                threading.Thread(
                    target=self.handle_client_message,
                    args=(message, addr),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Error: {e}")
    
    def handle_client_message(self, message: Dict, addr: tuple):
        """Handle incoming message from a client"""
        msg_type = message.get('type')
        
        if msg_type == 'join':
            self.handle_player_join(message, addr)
        elif msg_type == 'start_game':
            self.handle_start_game(message)
        elif msg_type == 'roll_dice':
            self.handle_roll_dice(message)
        elif msg_type == 'move':
            self.handle_player_move(message)
        elif msg_type == 'buy_property':
            self.handle_buy_property(message)
    
    def handle_player_join(self, message: Dict, addr: tuple):
        """Handle a player joining the game"""
        with self.lock:
            player_name = message.get('player_name')
            self.players[player_name] = addr
            print(f"Player '{player_name}' joined from {addr}")
            print(f"Players connected: {len(self.players)}")
            
            # Send acknowledgement
            response = {
                'type': 'join_ack',
                'status': 'success',
                'connected_players': list(self.players.keys())
            }
            self.send_to_client(addr, response)
    
    def handle_start_game(self, message: Dict):
        """Handle game start request"""
        with self.lock:
            player_names = list(self.players.keys())
            
            if len(player_names) < 2:
                print("Error: At least 2 players required")
                return
            
            self.game = Game(player_names)
            self.game_started = True
            print(f"\nGame started with {len(player_names)} players!")
            print(f"Players: {', '.join(player_names)}\n")
            
            # Broadcast game start to all clients
            response = {
                'type': 'game_started',
                'game_state': self.game.get_game_state()
            }
            self.broadcast(response)
    
    def handle_roll_dice(self, message: Dict):
        """Handle dice roll"""
        if not self.game_started:
            return
        
        with self.lock:
            die1, die2 = self.game.roll_dice()
            total = die1 + die2
            
            response = {
                'type': 'dice_rolled',
                'die1': die1,
                'die2': die2,
                'total': total,
                'is_doubles': die1 == die2
            }
            self.broadcast(response)
    
    def handle_player_move(self, message: Dict):
        """Handle player movement"""
        if not self.game_started:
            return
        
        with self.lock:
            spaces = message.get('spaces')
            self.game.move_player(spaces)
            
            # Update all clients
            response = {
                'type': 'game_state_update',
                'game_state': self.game.get_game_state()
            }
            self.broadcast(response)
    
    def handle_buy_property(self, message: Dict):
        """Handle property purchase"""
        if not self.game_started:
            return
        
        with self.lock:
            player = self.game.get_current_player()
            # Property purchase logic would go here
            
            response = {
                'type': 'game_state_update',
                'game_state': self.game.get_game_state()
            }
            self.broadcast(response)
    
    def send_to_client(self, addr: tuple, data: Dict):
        """Send a message to a specific client"""
        try:
            message = json.dumps(data).encode('utf-8')
            self.server_socket.sendto(message, addr)
        except Exception as e:
            print(f"Error sending to {addr}: {e}")
    
    def broadcast(self, data: Dict):
        """Send a message to all connected clients"""
        message = json.dumps(data).encode('utf-8')
        for player_name, addr in self.players.items():
            try:
                self.server_socket.sendto(message, addr)
            except Exception as e:
                print(f"Error broadcasting to {addr}: {e}")


if __name__ == '__main__':
    server = GameServer()
    server.start()
