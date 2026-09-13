"""Dice class for Monopoly game"""

import random


class Dice:
    """Represents a pair of dice"""
    
    def __init__(self):
        self.last_roll = (0, 0)
    
    def roll(self) -> tuple:
        """Roll two dice and return the result"""
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.last_roll = (die1, die2)
        return (die1, die2)
    
    def is_doubles(self) -> bool:
        """Check if the last roll was doubles"""
        return self.last_roll[0] == self.last_roll[1]
    
    def get_total(self) -> int:
        """Get the total of the last roll"""
        return sum(self.last_roll)
