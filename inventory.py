"""
inventory.py - Compatibility layer
Wraps the unified inventory system for backward compatibility.
"""

import pygame
import settings
import random

# Import from the new unified system
from ui.inventoryui import (
    Item, 
    make_medkit, 
    make_bandage, 
    make_ammo_pistol, 
    make_pistol, 
    make_melee,
    InventoryContainer,
    PlayerInventory,
    ChestContainer
)

# For backward compatibility with old code that expects these
def get_bullet_texture():
    """Legacy function for bullet texture."""
    return None

# Re-export commonly used functions
__all__ = [
    'Item',
    'make_medkit', 
    'make_bandage', 
    'make_ammo_pistol', 
    'make_pistol', 
    'make_melee',
    'InventoryContainer',
    'PlayerInventory',
    'ChestContainer'
]