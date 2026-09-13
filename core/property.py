"""Property class for Monopoly game"""

from typing import Dict, Optional


class Property:
    """Represents a property on the board"""
    
    RENT_MULTIPLIERS = {
        1: 1,
        2: 2,
        3: 3,
        4: 5,
        5: 8,
        'hotel': 11
    }
    
    def __init__(self, property_id: int, name: str, price: int, color: str, property_type: str):
        self.property_id = property_id
        self.name = name
        self.price = price
        self.color = color
        self.property_type = property_type  # 'street', 'railroad', 'utility', 'special'
        self.owner: Optional[str] = None
        self.houses = 0
        self.hotels = 0
        self.is_mortgaged = False
    
    def buy(self, player_name: str) -> None:
        """Set the owner of the property"""
        self.owner = player_name
    
    def calculate_rent(self, dice_roll: int = 0) -> int:
        """Calculate rent amount based on property type and improvements"""
        if self.owner is None or self.is_mortgaged:
            return 0
        
        if self.property_type == 'special':
            return 0
        
        elif self.property_type == 'utility':
            # Utilities: 4x or 10x the dice roll
            return dice_roll * 4  # Simplified; could be 10x with 2 utilities
        
        elif self.property_type == 'railroad':
            # Railroads: $25, $50, $100, or $200 depending on how many owned
            return 25 * (2 ** (self.houses))  # Simplified
        
        elif self.property_type == 'street':
            if self.hotels > 0:
                return self.price * self.RENT_MULTIPLIERS['hotel']
            elif self.houses > 0:
                return self.price * self.RENT_MULTIPLIERS[self.houses]
            else:
                return self.price // 10  # Base rent is 1/10 of purchase price
        
        return 0
    
    def add_house(self) -> bool:
        """Add a house. Return True if successful"""
        if self.houses < 4:
            self.houses += 1
            return True
        return False
    
    def add_hotel(self) -> bool:
        """Add a hotel (replaces houses). Return True if successful"""
        if self.houses == 4 and self.hotels == 0:
            self.houses = 0
            self.hotels = 1
            return True
        return False
    
    def mortgage(self) -> int:
        """Mortgage the property and return the mortgage value"""
        if not self.is_mortgaged:
            self.is_mortgaged = True
            return self.price // 2
        return 0
    
    def unmortgage(self, cost: int) -> bool:
        """Unmortgage the property. Return True if successful"""
        if self.is_mortgaged and cost == self.price // 2:
            self.is_mortgaged = False
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convert property to dictionary for serialization"""
        return {
            'id': self.property_id,
            'name': self.name,
            'price': self.price,
            'color': self.color,
            'type': self.property_type,
            'owner': self.owner,
            'houses': self.houses,
            'hotels': self.hotels,
            'mortgaged': self.is_mortgaged
        }
