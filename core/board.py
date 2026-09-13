"""Board class for Monopoly game"""

from typing import List
from .property import Property


class Board:
    """Represents the Monopoly board"""
    
    BOARD_SIZE = 40
    
    def __init__(self):
        self.properties = self._create_board()
    
    def _create_board(self) -> List[Property]:
        """Create the standard Monopoly board"""
        properties = []
        
        # Define board spaces (40 total)
        board_data = [
            # (name, price, color, position_type)
            ('GO', 0, 'special', 'corner'),
            ('Mediterranean Avenue', 60, 'brown', 'street'),
            ('Community Chest', 0, 'special', 'card'),
            ('Baltic Avenue', 60, 'brown', 'street'),
            ('Income Tax', 0, 'special', 'tax'),
            ('Reading Railroad', 200, 'railroad', 'railroad'),
            ('Oriental Avenue', 100, 'light_blue', 'street'),
            ('Chance', 0, 'special', 'card'),
            ('Vermont Avenue', 100, 'light_blue', 'street'),
            ('Connecticut Avenue', 120, 'light_blue', 'street'),
            ('JUST VISITING', 0, 'special', 'corner'),
            ('St. Charles Place', 140, 'pink', 'street'),
            ('Electric Company', 150, 'utility', 'utility'),
            ('States Avenue', 140, 'pink', 'street'),
            ('Virginia Avenue', 160, 'pink', 'street'),
            ('Pennsylvania Railroad', 200, 'railroad', 'railroad'),
            ('St. James Place', 180, 'orange', 'street'),
            ('Community Chest', 0, 'special', 'card'),
            ('Tennessee Avenue', 180, 'orange', 'street'),
            ('New York Avenue', 200, 'orange', 'street'),
            ('Free Parking', 0, 'special', 'corner'),
            ('Kentucky Avenue', 220, 'red', 'street'),
            ('Chance', 0, 'special', 'card'),
            ('Indiana Avenue', 220, 'red', 'street'),
            ('Illinois Avenue', 240, 'red', 'street'),
            ('B&O Railroad', 200, 'railroad', 'railroad'),
            ('Atlantic Avenue', 260, 'yellow', 'street'),
            ('Ventnor Avenue', 260, 'yellow', 'street'),
            ('Water Works', 150, 'utility', 'utility'),
            ('Marvin Gardens', 280, 'yellow', 'street'),
            ('GO TO JAIL', 0, 'special', 'corner'),
            ('Pacific Avenue', 300, 'green', 'street'),
            ('North Carolina Avenue', 300, 'green', 'street'),
            ('Community Chest', 0, 'special', 'card'),
            ('Pennsylvania Avenue', 320, 'green', 'street'),
            ('Short Line', 200, 'railroad', 'railroad'),
            ('Chance', 0, 'special', 'card'),
            ('Park Place', 350, 'dark_blue', 'street'),
            ('Luxury Tax', 0, 'special', 'tax'),
            ('Boardwalk', 400, 'dark_blue', 'street'),
        ]
        
        for idx, (name, price, color, prop_type) in enumerate(board_data):
            prop = Property(
                property_id=idx,
                name=name,
                price=price,
                color=color,
                property_type=prop_type
            )
            properties.append(prop)
        
        return properties
    
    def get_property(self, position: int) -> Property:
        """Get property at a given position"""
        return self.properties[position % self.BOARD_SIZE]
