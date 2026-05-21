### шар сумісності зроблений з куска старого коду, потім прибрати

import pygame
import settings
import random

# імпорт з нової уніфікованої системи
from ui.inventoryui import (
    Item, 
    make_medkit,
    make_ai2,
    make_bandage, 
    make_ammo_pistol, 
    make_pistol, 
    make_melee,
    InventoryContainer,
    PlayerInventory,
    ChestContainer
)


# реекспорт функцій для зручності
__all__ = [
    'Item',
    'make_medkit',
    'make_ai2', 
    'make_bandage', 
    'make_ammo_pistol', 
    'make_pistol', 
    'make_melee',
    'InventoryContainer',
    'PlayerInventory',
    'ChestContainer'
]