"""Player class for Monopoly game"""

from typing import List, Dict


class Player:
    """Represents a player in the game"""
    
    def __init__(self, name: str, starting_money: int):
        self.name = name
        self.money = starting_money
        self.position = 0  # Position on board (0-39)
        self.owned_properties: List[int] = []  # Property IDs
        self.in_jail = False
        self.jail_turns = 0
        self.houses_owned = 0
        self.hotels_owned = 0
    
    def move(self, spaces: int, board_size: int) -> bool:
        """Move player forward and return True if passed GO"""
        passed_go = False
        self.position += spaces
        
        if self.position >= board_size:
            self.position %= board_size
            passed_go = True
            self.collect_salary()  # Collect $200 for passing GO
        
        return passed_go
    
    def collect_salary(self) -> None:
        """Collect $200 salary for passing GO"""
        self.money += 200
    
    def add_money(self, amount: int) -> None:
        """Add money to player's balance"""
        self.money += amount
    
    def pay_money(self, amount: int) -> bool:
        """Pay money from player's balance. Return True if successful"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def buy_property(self, property_id: int, price: int) -> bool:
        """Buy a property. Return True if successful"""
        if self.pay_money(price):
            self.owned_properties.append(property_id)
            return True
        return False
    
    def is_bankrupt(self) -> bool:
        """Check if player is bankrupt"""
        return self.money < 0
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for serialization"""
        return {
            'name': self.name,
            'money': self.money,
            'position': self.position,
            'owned_properties': self.owned_properties,
            'in_jail': self.in_jail,
            'houses': self.houses_owned,
            'hotels': self.hotels_owned,
            'is_bankrupt': self.is_bankrupt()
        }
