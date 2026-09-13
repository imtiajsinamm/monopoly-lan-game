"""Main game logic for Monopoly"""

from typing import List, Dict, Optional
from .player import Player
from .board import Board
from .dice import Dice


class Game:
    """Main game controller"""
    
    STARTING_MONEY = 1500
    MAX_PLAYERS = 6
    
    def __init__(self, player_names: List[str]):
        if len(player_names) < 2 or len(player_names) > self.MAX_PLAYERS:
            raise ValueError(f"Game requires 2-{self.MAX_PLAYERS} players")
        
        self.players: List[Player] = [
            Player(name, self.STARTING_MONEY) for name in player_names
        ]
        self.board = Board()
        self.dice = Dice()
        self.current_player_index = 0
        self.game_over = False
        self.winner: Optional[Player] = None
    
    def get_current_player(self) -> Player:
        """Get the player whose turn it is"""
        return self.players[self.current_player_index]
    
    def roll_dice(self) -> tuple:
        """Roll the dice and return the result"""
        return self.dice.roll()
    
    def move_player(self, spaces: int) -> None:
        """Move current player forward on the board"""
        player = self.get_current_player()
        player.move(spaces, len(self.board.properties))
    
    def next_turn(self) -> None:
        """Move to the next player's turn"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.check_game_over()
    
    def check_game_over(self) -> None:
        """Check if the game is over (only one player with money left)"""
        active_players = [p for p in self.players if not p.is_bankrupt()]
        
        if len(active_players) == 1:
            self.game_over = True
            self.winner = active_players[0]
    
    def get_game_state(self) -> Dict:
        """Return the current game state"""
        return {
            'current_player': self.get_current_player().name,
            'players': [p.to_dict() for p in self.players],
            'game_over': self.game_over,
            'winner': self.winner.name if self.winner else None,
            'board_properties': [prop.to_dict() for prop in self.board.properties]
        }
