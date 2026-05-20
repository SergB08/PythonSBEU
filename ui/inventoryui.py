"""
ui/inventory.py

Full inventory system:
  - 3×5 backpack grid (15 slots)
  - 6 equipment slots: Head, Chest, Legs, Feet, Primary, Secondary
  - Minecraft-style chest (3×5 grid) that opens on interact
  - Drag & drop between all grids
  - [I] or [Tab] to toggle inventory
  - [E] near chest to open/close chest UI
"""

import pygame
import settings

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
C_CHEST     = (160, 120, 40,  255)
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
    def __init__(self, name: str, color=(120, 180, 120), icon=None,
                 stackable=False, count=1, eq_slot=None):
        self.name      = name
        self.color     = color
        self.icon      = icon       # pygame.Surface or None
        self.stackable = stackable
        self.count     = count
        self.eq_slot   = eq_slot    # None or one of EQ_SLOTS strings

    def draw_in_slot(self, screen, rect: pygame.Rect, alpha=255):
        """Draw item icon/colour swatch inside a slot rect."""
        surf = pygame.Surface((rect.w - 8, rect.h - 8), pygame.SRCALPHA)
        surf.set_alpha(alpha)
        if self.icon:
            scaled = pygame.transform.smoothscale(self.icon, surf.get_size())
            surf.blit(scaled, (0, 0))
        else:
            surf.fill((*self.color, alpha))
        screen.blit(surf, (rect.x + 4, rect.y + 4))
        if self.stackable and self.count > 1:
            cnt = _font(18, True).render(str(self.count), True, (255, 255, 255))
            screen.blit(cnt, (rect.right - cnt.get_width() - 4,
                              rect.bottom - cnt.get_height() - 2))


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


# ── Main Inventory UI ──────────────────────────────────────────────────────
class InventoryUI:
    """
    Draws the player inventory panel + equipment slots.
    Call .toggle() on [I]/[Tab], .handle_event() each frame.
    """

    def __init__(self):
        self.open       = False
        self._drag_item: Item | None = None
        self._drag_src:  Slot | None = None   # slot we dragged from
        self._tooltip   = ""

        self._build_layout()

    # ── layout ─────────────────────────────────────────────────────────── #

    def _build_layout(self):
        sw, sh = settings.WIDTH, settings.HEIGHT

        # ── Backpack panel (right side) ────────────────────────────────
        bw = PANEL_PAD * 2 + INV_COLS * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        bh = PANEL_PAD * 2 + INV_ROWS * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        bx = sw - bw - 30
        by = sh // 2 - bh // 2

        self.inv_panel  = pygame.Rect(bx, by, bw, bh)
        self.inv_slots  = _make_grid(bx + PANEL_PAD,
                                     by + PANEL_PAD + 30,
                                     INV_COLS, INV_ROWS)

        # ── Equipment panel (left of backpack) ─────────────────────────
        eq_cols = 2
        eq_rows = 3
        ew = PANEL_PAD * 2 + eq_cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        eh = PANEL_PAD * 2 + eq_rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        ex = bx - ew - 20
        ey = by

        self.eq_panel  = pygame.Rect(ex, ey, ew, eh)
        self.eq_slots  = _make_grid(ex + PANEL_PAD,
                                    ey + PANEL_PAD + 30,
                                    eq_cols, eq_rows,
                                    eq=True, labels=EQ_SLOTS)

        self.all_slots = self.inv_slots + self.eq_slots

    def toggle(self):
        self.open = not self.open
        if not self.open:
            self._cancel_drag()

    def _cancel_drag(self):
        if self._drag_item and self._drag_src:
            self._drag_src.item = self._drag_item
        self._drag_item = None
        self._drag_src  = None

    # ── public helpers ─────────────────────────────────────────────────── #

    def add_item(self, item: Item) -> bool:
        """Try to place item in first empty inv slot. Returns True on success."""
        for slot in self.inv_slots:
            if slot.item is None:
                slot.item = item
                return True
        return False

    def get_equipped(self, slot_name: str) -> "Item | None":
        for s in self.eq_slots:
            if s.label == slot_name:
                return s.item
        return None

    # ── events ─────────────────────────────────────────────────────────── #

    def handle_event(self, event):
        if not self.open:
            return
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slot in self.all_slots:
                if slot.hovered(mx, my) and slot.item:
                    self._drag_item = slot.item
                    self._drag_src  = slot
                    slot.item = None
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_item:
                placed = False
                for slot in self.all_slots:
                    if slot.hovered(mx, my):
                        # Equipment slot: only accept matching item
                        if slot.eq and self._drag_item.eq_slot != slot.label:
                            break
                        if slot.item is None:
                            slot.item = self._drag_item
                        else:
                            # Swap
                            slot.item, self._drag_src.item = \
                                self._drag_item, slot.item
                        placed = True
                        break
                if not placed:
                    self._drag_src.item = self._drag_item
                self._drag_item = None
                self._drag_src  = None

    # ── draw ───────────────────────────────────────────────────────────── #

    def draw(self, screen):
        if not self.open:
            return
        mx, my = pygame.mouse.get_pos()

        for panel, title in [(self.eq_panel,  "EQUIPMENT"),
                              (self.inv_panel, "BACKPACK")]:
            surf = pygame.Surface(panel.size, pygame.SRCALPHA)
            surf.fill(C_BG)
            screen.blit(surf, panel.topleft)
            pygame.draw.rect(screen, C_BORDER, panel, 2, border_radius=8)
            t = _font(26, True).render(title, True, C_TEXT)
            screen.blit(t, (panel.x + PANEL_PAD, panel.y + PANEL_PAD))

        for slot in self.all_slots:
            slot.draw(screen, mx, my)

        # Drag ghost
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
                self._tooltip = slot.item.name
        if self._tooltip:
            t = _font(22, True).render(self._tooltip, True, C_TEXT)
            tx = min(mx + 14, settings.WIDTH  - t.get_width()  - 4)
            ty = min(my + 14, settings.HEIGHT - t.get_height() - 4)
            bg = pygame.Surface((t.get_width() + 10, t.get_height() + 6),
                                 pygame.SRCALPHA)
            bg.fill((20, 20, 20, 200))
            screen.blit(bg, (tx - 5, ty - 3))
            screen.blit(t, (tx, ty))

        # Hint
        hint = _font(20).render("[I] / [Tab] Close  |  Drag to move items",
                                 True, C_TEXT_DIM)
        screen.blit(hint, (self.inv_panel.x,
                            self.inv_panel.bottom + 8))


# ── Chest UI ───────────────────────────────────────────────────────────────
class ChestUI:
    """
    Minecraft-style chest: 3×5 grid, opens near chest object.
    Items can be dragged between chest and player inventory.
    """

    CHEST_COLS = 5
    CHEST_ROWS = 3

    def __init__(self):
        self.open       = False
        self._slots: list[Slot] = []
        self._panel     = pygame.Rect(0, 0, 0, 0)
        self._drag_item: Item | None = None
        self._drag_src:  Slot | None = None
        self._inv_ref:   InventoryUI | None = None
        self._build()

    def _build(self):
        sw, sh = settings.WIDTH, settings.HEIGHT
        cols, rows = self.CHEST_COLS, self.CHEST_ROWS
        pw = PANEL_PAD * 2 + cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        ph = PANEL_PAD * 2 + rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD + 36
        px = sw // 2 - pw // 2
        py = sh // 2 - ph // 2 - 60
        self._panel  = pygame.Rect(px, py, pw, ph)
        self._slots  = _make_grid(px + PANEL_PAD,
                                   py + PANEL_PAD + 30,
                                   cols, rows)

    def open_chest(self, inv: InventoryUI):
        self.open     = True
        self._inv_ref = inv
        inv.open      = True      # auto-open player inventory too

    def close(self):
        self.open = False
        self._cancel_drag()

    def _cancel_drag(self):
        if self._drag_item and self._drag_src:
            self._drag_src.item = self._drag_item
        self._drag_item = None
        self._drag_src  = None

    def _all_slots(self):
        extra = self._inv_ref.all_slots if self._inv_ref else []
        return self._slots + extra

    def handle_event(self, event):
        if not self.open:
            return
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slot in self._all_slots():
                if slot.hovered(mx, my) and slot.item:
                    self._drag_item = slot.item
                    self._drag_src  = slot
                    slot.item = None
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag_item:
                placed = False
                for slot in self._all_slots():
                    if slot.hovered(mx, my):
                        if slot.eq and self._drag_item.eq_slot != slot.label:
                            break
                        if slot.item is None:
                            slot.item = self._drag_item
                        else:
                            slot.item, self._drag_src.item = \
                                self._drag_item, slot.item
                        placed = True
                        break
                if not placed:
                    self._drag_src.item = self._drag_item
                self._drag_item = None
                self._drag_src  = None

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_ESCAPE):
                self.close()

    def draw(self, screen):
        if not self.open:
            return
        mx, my = pygame.mouse.get_pos()

        surf = pygame.Surface(self._panel.size, pygame.SRCALPHA)
        surf.fill(C_BG)
        screen.blit(surf, self._panel.topleft)
        pygame.draw.rect(screen, C_CHEST,  self._panel, 3, border_radius=8)

        t = _font(26, True).render("CHEST", True, (220, 180, 80))
        screen.blit(t, (self._panel.x + PANEL_PAD, self._panel.y + PANEL_PAD))

        for slot in self._slots:
            slot.draw(screen, mx, my)

        if self._drag_item:
            self._drag_item.draw_in_slot(
                screen,
                pygame.Rect(mx - SLOT_SIZE // 2, my - SLOT_SIZE // 2,
                            SLOT_SIZE, SLOT_SIZE),
                alpha=180
            )

        hint = _font(20).render("[E] / [Esc] Close chest",
                                 True, C_TEXT_DIM)
        screen.blit(hint, (self._panel.x,
                            self._panel.bottom + 6))