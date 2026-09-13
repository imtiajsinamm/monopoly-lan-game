"""WebSocket server for Monopoly LAN game with room/lobby system"""

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import json
import random
import string
from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'monopoly-secret-key'
CORS(app)
sio = SocketIO(app, cors_allowed_origins="*")

# Store active rooms
ROOMS: Dict[str, dict] = {}

class GameRoom:
    """Represents a game room/lobby"""
    
    def __init__(self, room_code: str, host_name: str, max_players: int = 6):
        self.room_code = room_code
        self.host_name = host_name
        self.max_players = max_players
        self.players: Dict[str, dict] = {}  # player_id -> {name, sid, ready}
        self.game: Optional[Game] = None
        self.game_started = False
        self.created_at = None
    
    def add_player(self, player_id: str, player_name: str, sid: str) -> bool:
        """Add a player to the room"""
        if len(self.players) >= self.max_players:
            return False
        
        self.players[player_id] = {
            'name': player_name,
            'sid': sid,
            'ready': False
        }
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the room"""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def get_players_list(self) -> List[dict]:
        """Get list of players"""
        return [
            {
                'id': pid,
                'name': p['name'],
                'ready': p['ready'],
                'is_host': pid == self.host_name
            }
            for pid, p in self.players.items()
        ]
    
    def is_full(self) -> bool:
        """Check if room is full"""
        return len(self.players) >= self.max_players
    
    def can_start(self) -> bool:
        """Check if game can start (2+ players, all ready)"""
        return len(self.players) >= 2 and all(p['ready'] for p in self.players.values())
    
    def start_game(self) -> bool:
        """Start the game"""
        if not self.can_start():
            return False
        
        player_names = [p['name'] for p in self.players.values()]
        self.game = Game(player_names)
        self.game_started = True
        return True


def generate_room_code(length: int = 5) -> str:
    """Generate a random room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_room(room_code: str) -> Optional[GameRoom]:
    """Get a room by code"""
    return ROOMS.get(room_code)


# ==================== Socket Events ====================

@sio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected', 'sid': request.sid})


@sio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    
    # Remove player from any room they're in
    for room_code, room in list(ROOMS.items()):
        for player_id, player in list(room.players.items()):
            if player['sid'] == request.sid:
                room.remove_player(player_id)
                print(f"Player {player['name']} removed from room {room_code}")
                
                # Notify other players
                sio.emit('player_left', {
                    'player_name': player['name'],
                    'players': room.get_players_list()
                }, room=room_code)
                
                # Delete room if empty
                if len(room.players) == 0:
                    del ROOMS[room_code]
                    print(f"Room {room_code} deleted (empty)")
                break


@sio.on('create_room')
def handle_create_room(data):
    """Create a new game room"""
    player_name = data.get('player_name', 'Player')
    
    # Generate unique room code
    room_code = generate_room_code()
    while room_code in ROOMS:
        room_code = generate_room_code()
    
    # Create room
    room = GameRoom(room_code, player_name)
    room.add_player(player_name, player_name, request.sid)
    ROOMS[room_code] = room
    
    # Join socket room
    join_room(room_code)
    
    print(f"Room created: {room_code} by {player_name}")
    
    emit('room_created', {
        'room_code': room_code,
        'status': 'success',
        'message': f'Room created! Share code {room_code} with friends.',
        'players': room.get_players_list()
    })


@sio.on('join_room')
def handle_join_room(data):
    """Join an existing game room"""
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', 'Player')
    
    room = get_room(room_code)
    
    if not room:
        emit('join_room_error', {
            'status': 'error',
            'message': f'Room {room_code} not found'
        })
        return
    
    if room.game_started:
        emit('join_room_error', {
            'status': 'error',
            'message': 'Game already started in this room'
        })
        return
    
    if room.is_full():
        emit('join_room_error', {
            'status': 'error',
            'message': f'Room is full (max {room.max_players} players)'
        })
        return
    
    # Add player to room
    room.add_player(player_name, player_name, request.sid)
    join_room(room_code)
    
    print(f"Player {player_name} joined room {room_code}")
    
    # Notify all players in room
    sio.emit('player_joined', {
        'player_name': player_name,
        'players': room.get_players_list(),
        'room_code': room_code
    }, room=room_code)


@sio.on('set_ready')
def handle_set_ready(data):
    """Set player ready status"""
    room_code = data.get('room_code')
    player_name = data.get('player_name')
    ready = data.get('ready', False)
    
    room = get_room(room_code)
    if not room:
        return
    
    if player_name in room.players:
        room.players[player_name]['ready'] = ready
        print(f"Player {player_name} ready status: {ready}")
        
        # Notify all players
        sio.emit('room_updated', {
            'players': room.get_players_list(),
            'can_start': room.can_start()
        }, room=room_code)


@sio.on('start_game')
def handle_start_game(data):
    """Start the game"""
    room_code = data.get('room_code')
    player_name = data.get('player_name')
    
    room = get_room(room_code)
    if not room:
        emit('start_game_error', {'message': 'Room not found'})
        return
    
    # Only host can start
    if player_name != room.host_name:
        emit('start_game_error', {'message': 'Only host can start the game'})
        return
    
    # Check if game can start
    if not room.can_start():
        emit('start_game_error', {'message': 'Not all players are ready'})
        return
    
    # Start game
    if room.start_game():
        print(f"Game started in room {room_code}")
        sio.emit('game_started', {
            'status': 'success',
            'game_state': room.game.get_game_state()
        }, room=room_code)
    else:
        emit('start_game_error', {'message': 'Failed to start game'})


@sio.on('roll_dice')
def handle_roll_dice(data):
    """Handle dice roll"""
    room_code = data.get('room_code')
    player_name = data.get('player_name')
    
    room = get_room(room_code)
    if not room or not room.game_started:
        return
    
    # Verify it's the current player's turn
    current_player = room.game.get_current_player()
    if current_player.name != player_name:
        emit('error', {'message': 'Not your turn'})
        return
    
    die1, die2 = room.game.roll_dice()
    total = die1 + die2
    
    sio.emit('dice_rolled', {
        'player': player_name,
        'die1': die1,
        'die2': die2,
        'total': total,
        'is_doubles': die1 == die2
    }, room=room_code)


@sio.on('move_player')
def handle_move_player(data):
    """Handle player movement"""
    room_code = data.get('room_code')
    spaces = data.get('spaces')
    
    room = get_room(room_code)
    if not room or not room.game_started:
        return
    
    room.game.move_player(spaces)
    
    sio.emit('game_state_update', {
        'game_state': room.game.get_game_state()
    }, room=room_code)


@sio.on('end_turn')
def handle_end_turn(data):
    """Handle end of turn"""
    room_code = data.get('room_code')
    
    room = get_room(room_code)
    if not room or not room.game_started:
        return
    
    room.game.next_turn()
    
    sio.emit('game_state_update', {
        'game_state': room.game.get_game_state(),
        'turn_ended': True
    }, room=room_code)


@sio.on('get_game_state')
def handle_get_game_state(data):
    """Get current game state"""
    room_code = data.get('room_code')
    
    room = get_room(room_code)
    if not room:
        emit('error', {'message': 'Room not found'})
        return
    
    if room.game_started:
        emit('game_state', room.game.get_game_state())
    else:
        emit('lobby_state', {
            'room_code': room_code,
            'players': room.get_players_list(),
            'can_start': room.can_start()
        })


# ==================== HTTP Routes ====================

@app.route('/')
def index():
    return {
        'status': 'Monopoly LAN Game Server',
        'version': '1.0',
        'active_rooms': len(ROOMS)
    }


@app.route('/rooms')
def get_rooms():
    """Get list of active rooms"""
    rooms_list = []
    for code, room in ROOMS.items():
        if not room.game_started:
            rooms_list.append({
                'code': code,
                'host': room.host_name,
                'players': len(room.players),
                'max_players': room.max_players
            })
    return {'rooms': rooms_list}


@app.route('/room/<room_code>')
def get_room_info(room_code):
    """Get room information"""
    room = get_room(room_code.upper())
    
    if not room:
        return {'error': 'Room not found'}, 404
    
    return {
        'room_code': room.room_code,
        'host': room.host_name,
        'players': room.get_players_list(),
        'game_started': room.game_started,
        'can_start': room.can_start()
    }


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Monopoly LAN Game - WebSocket Server")
    print("="*60)
    print("Server running on http://localhost:5555")
    print("WebSocket connection: ws://localhost:5555")
    print("="*60 + "\n")
    
    sio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True)
