import pygame
import settings
import random
import assets


# ─────────────────────────────────────────────────────────────────────────────
#  ITEM DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

class Item:
    """Base item class. Replace color with image surface when textures are ready."""
    def __init__(self, name, item_type, color=(200, 200, 200), stackable=False, max_stack=1):
        self.name       = name
        self.item_type  = item_type   # "medkit" | "ammo_pistol" | "gun_pistol" | "melee" | "fist"
        self.color      = color
        self.stackable  = stackable
        self.max_stack  = max_stack
        self.count      = 1
        self.image      = None        # placeholder; drawn as colored rect if None

    def clone(self):
        c = Item(self.name, self.item_type, self.color, self.stackable, self.max_stack)
        c.count = self.count
        c.image = self.image
        return c
    
    def draw_in_slot(self, screen, rect, alpha=255):
        """Draw the item inside an inventory slot."""
        if alpha < 255:
            # Create a temporary surface with alpha
            temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            if self.image:
                padding = 8
                img_w = rect.width - padding * 2
                img_h = rect.height - padding * 2
                img = pygame.transform.scale(self.image, (img_w, img_h))
                temp_surf.blit(img, (padding, padding))
            else:
                inner = pygame.Rect(8, 8, rect.width - 16, rect.height - 16)
                pygame.draw.rect(temp_surf, self.color, inner, border_radius=4)
            
            if self.stackable and self.count > 1:
                font = pygame.font.SysFont(None, 18, bold=True)
                cnt = font.render(str(self.count), True, (255, 255, 255))
                temp_surf.blit(cnt, (rect.width - cnt.get_width() - 4,
                                    rect.height - cnt.get_height() - 4))
            
            temp_surf.set_alpha(alpha)
            screen.blit(temp_surf, rect.topleft)
        else:
            # Normal drawing (no alpha)
            if self.image:
                padding = 8
                img_w = rect.width - padding * 2
                img_h = rect.height - padding * 2
                img = pygame.transform.scale(self.image, (img_w, img_h))
                screen.blit(img, (rect.x + padding, rect.y + padding))
            else:
                inner = pygame.Rect(rect.x + 8, rect.y + 8,
                                    rect.width - 16, rect.height - 16)
                pygame.draw.rect(screen, self.color, inner, border_radius=4)
            
            if self.stackable and self.count > 1:
                font = pygame.font.SysFont(None, 18, bold=True)
                cnt = font.render(str(self.count), True, (255, 255, 255))
                screen.blit(cnt, (rect.right - cnt.get_width() - 4,
                                rect.bottom - cnt.get_height() - 4))


# ── Item textures cache ────────────────────────────────────────────────────── #
_MEDKIT_TEX = None
_BANDAGE_TEX = None
_AMMO_TEX = None


def _ensure_item_textures():
    """Lazily loads and unpacks item textures from assets if not already done."""
    global _MEDKIT_TEX, _BANDAGE_TEX, _AMMO_TEX
    if _MEDKIT_TEX is None:
        _MEDKIT_TEX, _BANDAGE_TEX, _AMMO_TEX = assets.load_item_sprites()


# ── Item factories ────────────────────────────────────────────────────────── #

def make_medkit():
    _ensure_item_textures()
    item = Item("Medkit", "medkit", color=(220, 60, 60), stackable=True, max_stack=5)
    item.image = _MEDKIT_TEX
    return item

def make_bandage():
    _ensure_item_textures()
    item = Item("Bandage", "bandage", color=(230, 230, 230), stackable=True, max_stack=5)
    item.image = _BANDAGE_TEX
    return item

def make_ammo_pistol(count=10):
    _ensure_item_textures()
    item = Item("Pistol Ammo", "ammo_pistol", color=(210, 170, 40), stackable=True, max_stack=60)
    item.count = count
    item.image = _AMMO_TEX
    return item

def make_pistol():
    item = Item("Pistol", "gun_pistol", color=(80, 80, 180))
    return item

def make_melee():
    item = Item("Knife", "melee", color=(160, 160, 160))
    return item


# ─────────────────────────────────────────────────────────────────────────────
#  SLOT
# ─────────────────────────────────────────────────────────────────────────────

SLOT_SIZE = 64
SLOT_PAD  = 6


class Slot:
    def __init__(self, x, y, label=""):
        self.rect  = pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)
        self.item  = None
        self.label = label
        self._font_small = None
        self._font_count = None

    def _fonts(self):
        if self._font_small is None:
            self._font_small = pygame.font.SysFont(None, 18, bold=True)
            self._font_count = pygame.font.SysFont(None, 22, bold=True)

    def draw(self, screen, highlight=False):
        self._fonts()
        border_col = (255, 200, 50) if highlight else (140, 140, 140)

        bg = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
        bg.fill((30, 30, 40, 200))
        screen.blit(bg, self.rect.topleft)
        pygame.draw.rect(screen, border_col, self.rect, 2, border_radius=4)

        if self.item:
            # Use the item's draw_in_slot method
            self.item.draw_in_slot(screen, self.rect)

        if self.label:
            lbl = self._font_small.render(self.label, True, (180, 180, 180))
            screen.blit(lbl, (self.rect.x + 3, self.rect.y + 3))


# ─────────────────────────────────────────────────────────────────────────────
#  INVENTORY  (TAB to open/close, 4×5 grid top-left)
# ─────────────────────────────────────────────────────────────────────────────

INV_COLS = 4
INV_ROWS = 5


class Inventory:
    def __init__(self):
        self.open    = False
        self._slots  = []
        self._font   = None
        self._rebuild()

    def _rebuild(self):
        self._slots = []
        ox = 30
        oy = 60
        for row in range(INV_ROWS):
            for col in range(INV_COLS):
                x = ox + col * (SLOT_SIZE + SLOT_PAD)
                y = oy + row * (SLOT_SIZE + SLOT_PAD)
                self._slots.append(Slot(x, y))

    def toggle(self):
        self.open = not self.open

    def add_item(self, item):
        # Try stacking first — exhaust ALL partial stacks before using empty slot
        if item.stackable:
            for slot in self._slots:
                if slot.item is None:
                    continue
                if (slot.item.item_type == item.item_type
                        and slot.item.count < slot.item.max_stack):
                    can_add = slot.item.max_stack - slot.item.count
                    add_amt = min(can_add, item.count)
                    slot.item.count += add_amt
                    item.count -= add_amt
                    if item.count <= 0:
                        return True
        # Find empty slot for remainder
        for slot in self._slots:
            if slot.item is None:
                slot.item = item
                return True
        return False

    def remove_item(self, item_type, count=1):
        removed = 0
        for slot in self._slots:
            if slot.item and slot.item.item_type == item_type:
                take = min(slot.item.count, count - removed)
                slot.item.count -= take
                removed += take
                if slot.item.count <= 0:
                    slot.item = None
                if removed >= count:
                    break
        return removed

    def count_item(self, item_type):
        total = 0
        for slot in self._slots:
            if slot.item and slot.item.item_type == item_type:
                total += slot.item.count
        return total

    def draw(self, screen):
        if not self.open:
            return
        if self._font is None:
            self._font = pygame.font.SysFont(None, 28, bold=True)

        pad = 12
        pw = INV_COLS * (SLOT_SIZE + SLOT_PAD) + pad * 2
        ph = INV_ROWS * (SLOT_SIZE + SLOT_PAD) + pad * 2 + 32
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((15, 15, 25, 210))
        screen.blit(panel, (30 - pad, 48))
        pygame.draw.rect(screen, (100, 100, 120),
                         pygame.Rect(30 - pad, 48, pw, ph), 2, border_radius=6)

        title = self._font.render("INVENTORY  [TAB]", True, (200, 200, 220))
        screen.blit(title, (30, 52))

        for slot in self._slots:
            slot.draw(screen)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_TAB:
                self.toggle()


# ─────────────────────────────────────────────────────────────────────────────
#  HOTBAR  (bottom-center: slot 1 = pistol, slot 2 = melee)
# ─────────────────────────────────────────────────────────────────────────────

class Hotbar:
    SLOTS = ["1", "2"]
    KEYS  = [pygame.K_1, pygame.K_2]

    def __init__(self):
        self.selected = 0
        self.slots    = []
        self._font    = None
        self._rebuild()
        self.slots[0].item = make_pistol()
        self.slots[1].item = make_melee()

    def _rebuild(self):
        self.slots = []
        n = len(self.SLOTS)
        w = n * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        ox = settings.WIDTH // 2 - w // 2
        oy = settings.HEIGHT - SLOT_SIZE - 16
        for i, lbl in enumerate(self.SLOTS):
            self.slots.append(Slot(ox + i * (SLOT_SIZE + SLOT_PAD), oy, lbl))

    def active_item(self):
        return self.slots[self.selected].item

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                for i, k in enumerate(self.KEYS):
                    if e.key == k:
                        self.selected = i

    def draw(self, screen):
        if self._font is None:
            self._font = pygame.font.SysFont(None, 20, bold=True)
        for i, slot in enumerate(self.slots):
            slot.draw(screen, highlight=(i == self.selected))
            hint = self._font.render(self.SLOTS[i], True, (160, 160, 160))
            screen.blit(hint, (slot.rect.centerx - hint.get_width() // 2,
                                slot.rect.bottom + 2))