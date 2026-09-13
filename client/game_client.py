"""Game client for Monopoly LAN game"""

import socket
import json
import threading
from typing import Dict, Optional
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GameClient:
    """Client for connecting to Monopoly game server"""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.server_address: Optional[tuple] = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('0.0.0.0', 0))  # Bind to any available port
        
        self.game_state: Optional[Dict] = None
        self.connected = False
        self.game_running = False
        self.lock = threading.Lock()
    
    def connect_to_server(self, server_ip: str, server_port: int = 5555) -> bool:
        """Connect to the game server"""
        try:
            self.server_address = (server_ip, server_port)
            
            # Send join message
            message = {
                'type': 'join',
                'player_name': self.player_name
            }
            self.send_message(message)
            
            # Start listening for messages
            threading.Thread(
                target=self.listen_for_messages,
                daemon=True
            ).start()
            
            # Wait for acknowledgement
            time.sleep(1)
            
            if self.connected:
                print(f"Successfully connected to server at {server_ip}:{server_port}")
                return True
            else:
                print("Failed to connect to server")
                return False
        
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def listen_for_messages(self):
        """Listen for incoming messages from the server"""
        while True:
            try:
                data, addr = self.client_socket.recvfrom(4096)
                message = json.loads(data.decode('utf-8'))
                self.handle_server_message(message)
            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
                break
    
    def handle_server_message(self, message: Dict):
        """Handle messages from the server"""
        msg_type = message.get('type')
        
        if msg_type == 'join_ack':
            self.connected = True
            print(f"Join acknowledged!")
            print(f"Connected players: {message.get('connected_players')}")
        
        elif msg_type == 'game_started':
            self.game_running = True
            self.game_state = message.get('game_state')
            print("\n" + "="*50)
            print("GAME STARTED!")
            print("="*50)
            self.display_game_state()
        
        elif msg_type == 'game_state_update':
            with self.lock:
                self.game_state = message.get('game_state')
                self.display_game_state()
        
        elif msg_type == 'dice_rolled':
            print(f"Dice rolled: {message.get('die1')} + {message.get('die2')} = {message.get('total')}")
            if message.get('is_doubles'):
                print("DOUBLES! Roll again!")
        
        else:
            print(f"Unknown message type: {msg_type}")
    
    def display_game_state(self):
        """Display the current game state"""
        if not self.game_state:
            return
        
        print(f"\nCurrent Player: {self.game_state.get('current_player')}")
        print(f"\nPlayers:")
        for player in self.game_state.get('players', []):
            status = "BANKRUPT" if player.get('is_bankrupt') else f"${player.get('money')}"
            print(f"  {player.get('name'):20} | Position: {player.get('position'):2} | Balance: {status:10}")
    
    def send_message(self, message: Dict):
        """Send a message to the server"""
        try:
            data = json.dumps(message).encode('utf-8')
            self.client_socket.sendto(data, self.server_address)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def roll_dice(self):
        """Request a dice roll"""
        message = {
            'type': 'roll_dice',
            'player_name': self.player_name
        }
        self.send_message(message)
    
    def move(self, spaces: int):
        """Move the player"""
        message = {
            'type': 'move',
            'player_name': self.player_name,
            'spaces': spaces
        }
        self.send_message(message)
    
    def buy_property(self, property_id: int):
        """Buy a property"""
        message = {
            'type': 'buy_property',
            'player_name': self.player_name,
            'property_id': property_id
        }
        self.send_message(message)


def main():
    """Main client loop"""
    print("\n" + "="*50)
    print("Monopoly LAN Game - Client")
    print("="*50)
    
    player_name = input("Enter your player name: ").strip()
    server_ip = input("Enter server IP address (default: 127.0.0.1): ").strip() or "127.0.0.1"
    
    client = GameClient(player_name)
    
    if not client.connect_to_server(server_ip):
        print("Failed to connect. Exiting.")
        return
    
    print("\nWaiting for game to start...")
    print("Commands: roll (roll dice), move <spaces> (move), buy <property_id> (buy property), quit (exit)")
    
    while True:
        try:
            command = input("\n> ").strip().lower().split()
            
            if not command:
                continue
            
            if command[0] == 'roll':
                client.roll_dice()
            
            elif command[0] == 'move' and len(command) > 1:
                try:
                    spaces = int(command[1])
                    client.move(spaces)
                except ValueError:
                    print("Invalid space count")
            
            elif command[0] == 'buy' and len(command) > 1:
                try:
                    prop_id = int(command[1])
                    client.buy_property(prop_id)
                except ValueError:
                    print("Invalid property ID")
            
            elif command[0] == 'quit':
                print("Goodbye!")
                break
            
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    main()
