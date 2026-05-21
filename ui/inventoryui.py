"""
ui/inventory.py

Unified inventory system for player and containers.
- Player inventory: 5x3 backpack + 6 equipment slots
- Container inventory: variable size (3x3 for chests)
- Drag & drop support between inventories
- Stackable items supported
"""

import pygame
import settings
import random

# ── Colours ────────────────────────────────────────────────────────────────
C_BG        = (28,  28,  28,  220)
C_PANEL     = (38,  38,  42,  255)
C_SLOT      = (55,  55,  60,  255)
C_SLOT_EQ   = (40,  50,  70,  255)
C_SLOT_HOV  = (80,  80,  90,  255)
C_SLOT_SEL  = (100, 140, 200, 255)
C_BORDER    = (90,  90,  100, 255)
C_BORDER_EQ = (80,  110, 160, 255)
C_TEXT      = (220, 220, 220)
C_TEXT_DIM  = (140, 140, 150)
C_CONTAINER = (160, 120, 40,  255)
C_DRAG      = (180, 200, 255, 200)

SLOT_SIZE   = 64
SLOT_PAD    = 6
PANEL_PAD   = 14
INV_COLS    = 5
INV_ROWS    = 3

EQ_SLOTS = ["Head", "Chest", "Legs", "Feet", "Primary", "Secondary"]

FONT_CACHE: dict = {}


def _font(size: int, bold: bool = False):
    key = (size, bold)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = pygame.font.SysFont(None, size, bold=bold)
    return FONT_CACHE[key]


# ── Item ───────────────────────────────────────────────────────────────────
class Item:
    def __init__(self, name: str, item_type: str = "misc", color=(120, 180, 120), 
                 image=None, stackable=False, count=1, eq_slot=None):
        self.name      = name
        self.item_type = item_type  # "medkit", "bandage", "ammo_pistol", "gun_pistol", "melee", "misc"
        self.color     = color
        self.image     = image       # pygame.Surface or None  # CHANGED: icon -> image
        self.stackable = stackable
        self.count     = count
        self.max_stack = 100 if item_type == "ammo_pistol" else (5 if item_type in ("medkit", "bandage") else 1)
        self.eq_slot   = eq_slot    # None or one of EQ_SLOTS strings

    def clone(self):
        """Create a copy of this item."""
        new = Item(self.name, self.item_type, self.color, self.image, 
                   self.stackable, self.count, self.eq_slot)
        new.max_stack = self.max_stack
        return new

    def draw_in_slot(self, screen, rect: pygame.Rect, alpha=255):
        """Draw item image/colour swatch inside a slot rect."""
        surf = pygame.Surface((rect.w - 8, rect.h - 8), pygame.SRCALPHA)
        surf.set_alpha(alpha)
        if self.image:
            scaled = pygame.transform.scale(self.image, surf.get_size())
            surf.blit(scaled, (0, 0))
        else:
            surf.fill((*self.color, alpha))
        screen.blit(surf, (rect.x + 4, rect.y + 4))
        if self.stackable and self.count > 1:
            cnt = _font(18, True).render(str(self.count), True, (255, 255, 255))
            screen.blit(cnt, (rect.right - cnt.get_width() - 4,
                              rect.bottom - cnt.get_height() - 2))


# ── Item factories ──────────────────────────────────────────────────────────
_MEDKIT_TEX = None
_BANDAGE_TEX = None
_AMMO_TEX = None


def _ensure_item_textures():
    """Lazily loads item textures from assets if not already done."""
    global _MEDKIT_TEX, _BANDAGE_TEX, _AMMO_TEX
    if _MEDKIT_TEX is None:
        try:
            import assets
            _MEDKIT_TEX, _BANDAGE_TEX, _AMMO_TEX = assets.load_item_sprites()
        except ImportError:
            pass


def make_medkit():
    _ensure_item_textures()
    return Item("Medkit", "medkit", color=(220, 60, 60), image=_MEDKIT_TEX, stackable=False, count=1)


def make_bandage():
    _ensure_item_textures()
    return Item("Bandage", "bandage", color=(230, 230, 230), image=_BANDAGE_TEX, stackable=False, count=1)


def make_ammo_pistol(count=10):
    _ensure_item_textures()
    return Item("Pistol Ammo", "ammo_pistol", color=(210, 170, 40), image=_AMMO_TEX, stackable=True, count=count)


def make_pistol():
    return Item("Pistol", "gun_pistol", color=(80, 80, 180), eq_slot="Primary")


def make_melee():
    return Item("Knife", "melee", color=(160, 160, 160), eq_slot="Secondary")


def make_fist():
    return Item("Fists", "melee", color=(200, 200, 200), stackable=False)


# ── Slot ───────────────────────────────────────────────────────────────────
class Slot:
    def __init__(self, rect: pygame.Rect, label: str = "", eq=False):
        self.rect  = rect
        self.label = label
        self.eq    = eq
        self.item: Item | None = None

    def hovered(self, mx, my):
        return self.rect.collidepoint(mx, my)

    def draw(self, screen, mx, my, selected=False):
        hov  = self.hovered(mx, my)
        col  = C_SLOT_EQ if self.eq else C_SLOT
        if hov:    col = C_SLOT_HOV
        if selected: col = C_SLOT_SEL

        pygame.draw.rect(screen, col,            self.rect, border_radius=6)
        border = C_BORDER_EQ if self.eq else C_BORDER
        pygame.draw.rect(screen, border,         self.rect, 2, border_radius=6)

        if self.label and self.item is None:
            lbl = _font(18).render(self.label, True, C_TEXT_DIM)
            screen.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                               self.rect.centery - lbl.get_height() // 2))

        if self.item:
            self.item.draw_in_slot(screen, self.rect)


# ── Grid helper ────────────────────────────────────────────────────────────
def _make_grid(origin_x, origin_y, cols, rows, eq=False, labels=None):
    slots = []
    for r in range(rows):
        for c in range(cols):
            x = origin_x + c * (SLOT_SIZE + SLOT_PAD)
            y = origin_y + r * (SLOT_SIZE + SLOT_PAD)
            lbl = ""
            if labels:
                idx = r * cols + c
                lbl = labels[idx] if idx < len(labels) else ""
            slots.append(Slot(pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE),
                              label=lbl, eq=eq))
    return slots


# ── Base Inventory Container ───────────────────────────────────────────────
class InventoryContainer:
    """Base class for inventory containers (player inventory, chests, etc.)"""
    
    def __init__(self, cols: int, rows: int, title: str = "INVENTORY", 
                 slot_color: tuple = C_SLOT):
        self.cols = cols
        self.rows = rows
        self.title = title
        self.slot_color = slot_color
        self._slots: list[Slot] = []
        self._panel: pygame.Rect | None = None
        self._build_layout()
    
    def _build_layout(self):
        """Build slot grid layout. Override for custom positioning."""
        sw, sh = settings.WIDTH, settings.HEIGHT
        pw = PANEL_PAD * 2 + self.cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        ph = PANEL_PAD * 2 + self.rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        px = sw // 2 - pw // 2
        py = sh // 2 - ph // 2
        self._panel = pygame.Rect(px, py, pw, ph)
        self._slots = _make_grid(px + PANEL_PAD, py + PANEL_PAD + 30,
                                  self.cols, self.rows)
    
    def set_position(self, x: int, y: int):
        """Set custom panel position."""
        pw = PANEL_PAD * 2 + self.cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        ph = PANEL_PAD * 2 + self.rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        self._panel = pygame.Rect(x, y, pw, ph)
        self._slots = _make_grid(x + PANEL_PAD, y + PANEL_PAD + 30,
                                  self.cols, self.rows)
    
    @property
    def slots(self):
        return self._slots
    
    def add_item(self, item: Item) -> bool:
        """
        Add item to inventory. Handles stacking.
        Returns True if item was added (or partially added for stackable items).
        """
        if item.stackable:
            remaining = item.count
            
            # Try to add to existing stacks
            for slot in self._slots:
                if slot.item and slot.item.item_type == item.item_type:
                    space = slot.item.max_stack - slot.item.count
                    if space > 0:
                        add = min(space, remaining)
                        slot.item.count += add
                        remaining -= add
                        if remaining <= 0:
                            return True
            
            # If still remaining, try empty slots
            if remaining > 0:
                new_item = item.clone()
                new_item.count = remaining
                for slot in self._slots:
                    if slot.item is None:
                        slot.item = new_item
                        return True
            return remaining == 0  # True if all added, False if some left
        
        else:
            # Non-stackable: just find empty slot
            for slot in self._slots:
                if slot.item is None:
                    slot.item = item.clone()
                    return True
            return False
    
    def remove_item(self, item_type: str, count: int = 1) -> int:
        """Remove up to count items of given type. Returns actual amount removed."""
        removed = 0
        for slot in self._slots:
            if slot.item and slot.item.item_type == item_type:
                if slot.item.stackable:
                    take = min(slot.item.count, count - removed)
                    slot.item.count -= take
                    removed += take
                    if slot.item.count <= 0:
                        slot.item = None
                else:
                    slot.item = None
                    removed += 1
                if removed >= count:
                    break
        return removed
    
    def count_item(self, item_type: str) -> int:
        """Count total quantity of an item type in inventory."""
        total = 0
        for slot in self._slots:
            if slot.item and slot.item.item_type == item_type:
                total += slot.item.count if slot.item.stackable else 1
        return total
    
    def has_space_for(self, item: Item) -> bool:
        """Check if inventory has space for the item."""
        if item.stackable:
            # Check existing stacks
            for slot in self._slots:
                if slot.item and slot.item.item_type == item.item_type:
                    if slot.item.count < slot.item.max_stack:
                        return True
            # Check empty slots
            for slot in self._slots:
                if slot.item is None:
                    return True
            return False
        else:
            for slot in self._slots:
                if slot.item is None:
                    return True
            return False
    
    def clear(self):
        """Clear all slots."""
        for slot in self._slots:
            slot.item = None
    
    def draw(self, screen, mx: int, my: int, drag_item: Item | None = None):
        """Draw the inventory panel and slots."""
        if self._panel is None:
            return
        
        # Draw panel background
        surf = pygame.Surface(self._panel.size, pygame.SRCALPHA)
        surf.fill(C_BG)
        screen.blit(surf, self._panel.topleft)
        pygame.draw.rect(screen, self.slot_color, self._panel, 2, border_radius=8)
        
        # Draw title
        t = _font(26, True).render(self.title, True, C_TEXT)
        screen.blit(t, (self._panel.x + PANEL_PAD, self._panel.y + PANEL_PAD))
        
        # Draw slots
        for slot in self._slots:
            slot.draw(screen, mx, my)


# ── Player Inventory UI ─────────────────────────────────────────────────────
class PlayerInventory:
    """
    Player inventory: backpack (5x3) + equipment slots (2x3).
    Handles drag & drop between all slots.
    """
    
    def __init__(self):
        self.open = False
        self._drag_item: Item | None = None
        self._drag_src: Slot | None = None
        self._tooltip = ""
        self._backpack: InventoryContainer | None = None
        self._equipment: InventoryContainer | None = None
        self._build_layout()
    
    def _build_layout(self):
        sw, sh = settings.WIDTH, settings.HEIGHT
        
        # Backpack panel (right side)
        bw = PANEL_PAD * 2 + INV_COLS * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        bh = PANEL_PAD * 2 + INV_ROWS * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        bx = sw - bw - 30
        by = sh // 2 - bh // 2
        
        self._backpack = InventoryContainer(INV_COLS, INV_ROWS, "BACKPACK")
        self._backpack.set_position(bx, by)
        
        # Equipment panel (left of backpack)
        eq_cols = 2
        eq_rows = 3
        ew = PANEL_PAD * 2 + eq_cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        eh = PANEL_PAD * 2 + eq_rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        ex = bx - ew - 20
        ey = by
        
        self._equipment = InventoryContainer(eq_cols, eq_rows, "EQUIPMENT", slot_color=C_SLOT_EQ)
        self._equipment.set_position(ex, ey)
        
        # Set equipment slot labels
        for i, slot in enumerate(self._equipment.slots):
            if i < len(EQ_SLOTS):
                slot.label = EQ_SLOTS[i]
                slot.eq = True
    
    @property
    def inv_slots(self):
        """Convenience property to get all inventory slots."""
        return self._backpack.slots if self._backpack else []
    
    @property
    def all_slots(self):
        """All slots including equipment."""
        result = []
        if self._backpack:
            result.extend(self._backpack.slots)
        if self._equipment:
            result.extend(self._equipment.slots)
        return result
    
    def toggle(self):
        self.open = not self.open
        if not self.open:
            self._cancel_drag()
    
    def _cancel_drag(self):
        if self._drag_item and self._drag_src:
            self._drag_src.item = self._drag_item
        self._drag_item = None
        self._drag_src = None
    
    def add_item(self, item: Item) -> bool:
        """Add item to backpack inventory."""
        if self._backpack:
            return self._backpack.add_item(item)
        return False
    
    def remove_item(self, item_type: str, count: int = 1) -> int:
        """Remove items from backpack inventory."""
        if self._backpack:
            return self._backpack.remove_item(item_type, count)
        return 0
    
    def count_item(self, item_type: str) -> int:
        """Count items in backpack inventory."""
        if self._backpack:
            return self._backpack.count_item(item_type)
        return 0
    
    def get_equipped(self, slot_name: str) -> Item | None:
        """Get equipped item in a specific equipment slot."""
        if self._equipment:
            for slot in self._equipment.slots:
                if slot.label == slot_name:
                    return slot.item
        return None
    
    def handle_event(self, event):
        if not self.open:
            return
        
        mx, my = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slot in self.all_slots:
                if slot.hovered(mx, my) and slot.item:
                    self._drag_item = slot.item
                    self._drag_src = slot
                    slot.item = None
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_item:
                placed = False
                for slot in self.all_slots:
                    if slot.hovered(mx, my):
                        # Equipment slot: only accept if matching label or None
                        if slot.eq and slot.label:
                            if self._drag_item.eq_slot != slot.label:
                                break
                        if slot.item is None:
                            slot.item = self._drag_item
                        else:
                            # Swap items
                            slot.item, self._drag_src.item = self._drag_item, slot.item
                        placed = True
                        break
                if not placed:
                    self._drag_src.item = self._drag_item
                self._drag_item = None
                self._drag_src = None
    
    def draw(self, screen):
        if not self.open:
            return
        
        mx, my = pygame.mouse.get_pos()
        
        if self._backpack:
            self._backpack.draw(screen, mx, my)
        #if self._equipment: DISABLED FOR NOW
            #self._equipment.draw(screen, mx, my)
        
        # Draw equipment slots with special border ### DISABLED FOR NOW
        #if self._equipment:
        #    for slot in self._equipment.slots:
        #        slot.draw(screen, mx, my)
        
        # Draw backpack slots
        if self._backpack:
            for slot in self._backpack.slots:
                slot.draw(screen, mx, my)
        
        # Draw drag ghost
        if self._drag_item:
            self._drag_item.draw_in_slot(
                screen,
                pygame.Rect(mx - SLOT_SIZE // 2, my - SLOT_SIZE // 2,
                            SLOT_SIZE, SLOT_SIZE),
                alpha=180
            )
        
        # Tooltip
        self._tooltip = ""
        for slot in self.all_slots:
            if slot.hovered(mx, my) and slot.item:
                self._tooltip = f"{slot.item.name}"
                if slot.item.stackable and slot.item.count > 1:
                    self._tooltip += f" x{slot.item.count}"
        if self._tooltip:
            t = _font(22, True).render(self._tooltip, True, C_TEXT)
            tx = min(mx + 14, settings.WIDTH - t.get_width() - 4)
            ty = min(my + 14, settings.HEIGHT - t.get_height() - 4)
            bg = pygame.Surface((t.get_width() + 10, t.get_height() + 6),
                                 pygame.SRCALPHA)
            bg.fill((20, 20, 20, 200))
            screen.blit(bg, (tx - 5, ty - 3))
            screen.blit(t, (tx, ty))
        
        # Hint
        hint = _font(20).render("[I] / [Tab] Close  |  Drag to move items",
                                 True, C_TEXT_DIM)
        if self._backpack and self._backpack._panel:
            screen.blit(hint, (self._backpack._panel.x,
                                self._backpack._panel.bottom + 8))


# ── Chest Container UI ──────────────────────────────────────────────────────
class ChestContainer:
    """
    Standalone chest inventory: 3x3 grid.
    Used for safe room chest.
    """
    
    def __init__(self):
        self.open = False
        self._container: InventoryContainer | None = None
        self._drag_item: Item | None = None
        self._drag_src: Slot | None = None
        self._player_inv: PlayerInventory | None = None
        self._build()
    
    def _build(self):
        cols, rows = 3, 3
        self._container = InventoryContainer(cols, rows, "CHEST", slot_color=C_CONTAINER)
        # Position centered on screen
        sw, sh = settings.WIDTH, settings.HEIGHT
        pw = PANEL_PAD * 2 + cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        ph = PANEL_PAD * 2 + rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        px = sw // 2 - pw // 2
        py = sh // 2 - ph // 2 - 60
        self._container.set_position(px, py)
    
    def open_chest(self, player_inv: PlayerInventory):
        self.open = True
        self._player_inv = player_inv
        player_inv.open = True  # Auto-open player inventory too
    
    def close(self):
        self.open = False
        self._cancel_drag()
        if self._player_inv:
            self._player_inv.open = False
    
    def _cancel_drag(self):
        if self._drag_item and self._drag_src:
            self._drag_src.item = self._drag_item
        self._drag_item = None
        self._drag_src = None
    
    def _all_slots(self):
        """All draggable slots (chest + player inventory)."""
        result = []
        if self._container:
            result.extend(self._container.slots)
        if self._player_inv:
            result.extend(self._player_inv.all_slots)
        return result
    
    def add_item(self, item: Item) -> bool:
        """Add item to chest inventory."""
        if self._container:
            return self._container.add_item(item)
        return False
    
    def remove_item(self, item_type: str, count: int = 1) -> int:
        """Remove items from chest inventory."""
        if self._container:
            return self._container.remove_item(item_type, count)
        return 0
    
    def clear(self):
        """Clear chest contents."""
        if self._container:
            self._container.clear()
    
    def get_loot_items(self):
        """Get all items in chest as a list."""
        items = []
        if self._container:
            for slot in self._container.slots:
                if slot.item:
                    items.append(slot.item)
        return items
    
    def handle_event(self, event):
        if not self.open:
            return
        
        mx, my = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slot in self._all_slots():
                if slot.hovered(mx, my) and slot.item:
                    self._drag_item = slot.item
                    self._drag_src = slot
                    slot.item = None
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_item:
                placed = False
                for slot in self._all_slots():
                    if slot.hovered(mx, my):
                        # Equipment slot check
                        if slot.eq and slot.label:
                            if self._drag_item.eq_slot != slot.label:
                                break
                        if slot.item is None:
                            slot.item = self._drag_item
                        else:
                            # Swap items
                            slot.item, self._drag_src.item = self._drag_item, slot.item
                        placed = True
                        break
                if not placed:
                    self._drag_src.item = self._drag_item
                self._drag_item = None
                self._drag_src = None
        
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_ESCAPE):
                self.close()
    
    def draw(self, screen):
        if not self.open:
            return
        
        mx, my = pygame.mouse.get_pos()
        
        if self._container:
            self._container.draw(screen, mx, my)
        
        # Draw drag ghost
        if self._drag_item:
            self._drag_item.draw_in_slot(
                screen,
                pygame.Rect(mx - SLOT_SIZE // 2, my - SLOT_SIZE // 2,
                            SLOT_SIZE, SLOT_SIZE),
                alpha=180
            )
        
        # Hint
        hint = _font(20).render("[E] / [Esc] Close chest", True, C_TEXT_DIM)
        if self._container and self._container._panel:
            screen.blit(hint, (self._container._panel.x,
                                self._container._panel.bottom + 6))