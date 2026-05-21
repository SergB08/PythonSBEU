"""
ui/health.py

Project Zomboid-style health system.

Body parts: Head, Torso, L.Arm, R.Arm, L.Leg, R.Leg
Each part has hp (0-100), bleeding, fractured.

Hit-chance weights (must sum to 1.0):
  Torso  35%   <- biggest target
  L.Leg  15%
  R.Leg  15%
  L.Arm  12%
  R.Arm  12%
  Head   11%   <- hard to hit

Damage multipliers per part:
  Head   2.0x  <- dangerous but not instant-kill
  Torso  1.0x
  L.Arm  0.7x
  R.Arm  0.7x
  L.Leg  0.8x
  R.Leg  0.8x

Death: Head HP <= 0  OR  Torso HP <= 0
Every hit is guaranteed to deal at least 1 damage.
"""

import random
import pygame
import settings

# ── palette ────────────────────────────────────────────────────────────────
C_BG     = (28,  28,  28,  210)
C_BORDER = (90,  90, 100, 255)
C_TEXT   = (220, 220, 220)
C_DIM    = (140, 140, 150)
C_FULL   = (60,  200,  60)
C_MID    = (220, 180,  30)
C_LOW    = (220,  60,  40)
C_BLEED  = (200,  30,  30)
# C_FRAC   = (180, 160, 100)  # fractured — unused
C_MEDS_GLOW = (180, 220, 255, 80)   # highlight when dragging medicine item over a bar

FONT_CACHE: dict = {}


def _font(size, bold=False):
    key = (size, bold)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = pygame.font.SysFont(None, size, bold=bold)
    return FONT_CACHE[key]


def _hp_color(ratio):
    if ratio > 0.6:
        return C_FULL
    elif ratio > 0.3:
        return C_MID
    return C_LOW


# ── Hit-chance weights ─────────────────────────────────────────────────────
PART_HIT_WEIGHT = {
    "Torso": 0.35,
    "L.Leg": 0.15,
    "R.Leg": 0.15,
    "L.Arm": 0.12,
    "R.Arm": 0.12,
    "Head":  0.11,
}

# ── Damage multipliers per part ────────────────────────────────────────────
PART_DAMAGE_MULT = {
    "Head":  2.0,
    "Torso": 1.0,
    "L.Arm": 0.7,
    "R.Arm": 0.7,
    "L.Leg": 0.8,
    "R.Leg": 0.8,
}

# Death when any vital part reaches 0
VITAL_PARTS = {"Head", "Torso"}

PART_NAMES = ["Head", "Torso", "L.Arm", "R.Arm", "L.Leg", "R.Leg"]


def _random_part() -> str:
    parts   = list(PART_HIT_WEIGHT.keys())
    weights = [PART_HIT_WEIGHT[p] for p in parts]
    return random.choices(parts, weights=weights, k=1)[0]


# ── Body part ──────────────────────────────────────────────────────────────
class BodyPart:
    MAX_HP = 100

    def __init__(self, name: str):
        self.name      = name
        self.hp        = float(self.MAX_HP)
        self.bleeding  = False
        # self.fractured = False   # unused

    @property
    def alive(self):
        return self.hp > 0

    def take_damage(self, amount: float):
        self.hp = max(0.0, self.hp - amount)

    def heal(self, amount: float):
        self.hp = min(float(self.MAX_HP), self.hp + amount)

    def update(self, dt: float):
        pass

    @property
    def ratio(self):
        return self.hp / self.MAX_HP


# ── Full health model ──────────────────────────────────────────────────────
class BodyHealth:
    def __init__(self):
        self.parts: dict[str, BodyPart] = {n: BodyPart(n) for n in PART_NAMES}
        self.alive = True
        # self.sick   = False   # unused
        # self.tired  = False   # unused
        self._panel_open = False

        # Medicine item drag state
        self._dragging_meds = False
        self._drag_pos         = (0, 0)
        self._drag_item        = None   # Item reference from inventory
        self._drag_src_slot    = None   # Slot reference to remove from
        # Cached bar rects for hit-testing (populated in _draw_full_panel)
        self._bar_rects: dict[str, pygame.Rect] = {}

    # ── damage ─────────────────────────────────────────────────────────── #

    def take_damage(self, amount: float, part_name: str = "Torso"):
        if not self.alive:
            return
        part = self.parts.get(part_name, self.parts["Torso"])
        # If part is already at 0, redistribute to alive parts
        if part.hp <= 0:
            self.take_damage_any(amount)
            return
        mult  = PART_DAMAGE_MULT.get(part_name, 1.0)
        final = max(1.0, amount * mult)
        part.take_damage(final)
        if random.random() < 0.25:
            part.bleeding = True
        self._check_death()

    def take_damage_any(self, amount: float):
        if not self.alive:
            return
        # Only pick from parts that still have HP
        alive_parts = [n for n, p in self.parts.items() if p.hp > 0]
        if not alive_parts:
            return
        weights = [PART_HIT_WEIGHT.get(n, 0.1) for n in alive_parts]
        part_name = random.choices(alive_parts, weights=weights, k=1)[0]
        self.take_damage(amount, part_name)

    def heal_part(self, part_name: str, amount: float):
        part = self.parts.get(part_name)
        if part:
            part.heal(amount)
            part.bleeding = False

    def heal_all(self, amount: float = 9999):
        for part in self.parts.values():
            part.heal(amount)
            part.bleeding  = False
            # part.fractured = False   # unused
        self.alive = True
        # self.sick   = False   # unused
        # self.tired  = False   # unused

    def stop_bleeding(self, part_name: str):
        part = self.parts.get(part_name)
        if part:
            part.bleeding = False

    def _check_death(self):
        for name in VITAL_PARTS:
            if self.parts[name].hp <= 0:
                self.alive = False
                return

    # ── totals ─────────────────────────────────────────────────────────── #

    @property
    def total_hp(self):
        return sum(p.hp for p in self.parts.values())

    @property
    def max_total_hp(self):
        return BodyPart.MAX_HP * len(self.parts)

    @property
    def overall_ratio(self):
        return self.total_hp / self.max_total_hp

    # ── moodle helpers ─────────────────────────────────────────────────── #

    @property
    def in_pain(self):
        return any(p.hp < 70 for p in self.parts.values())

    @property
    def injured(self):
        return any(p.hp < 50 for p in self.parts.values())

    @property
    def bleeding(self):
        return any(p.bleeding for p in self.parts.values())

    # ── update ─────────────────────────────────────────────────────────── #

    def update(self, dt: float):
        for name, part in self.parts.items():
            if part.bleeding:
                if part.hp > 0:
                    part.hp = max(0.0, part.hp - 2.0 * dt)
                else:
                    # redistribute bleed damage to alive parts
                    alive_parts = [n for n, p in self.parts.items() if p.hp > 0]
                    if alive_parts:
                        weights = [PART_HIT_WEIGHT.get(n, 0.1) for n in alive_parts]
                        target = random.choices(alive_parts, weights=weights, k=1)[0]
                        self.parts[target].hp = max(0.0, self.parts[target].hp - 2.0 * dt)
        self._check_death()

    def toggle_panel(self):
        self._panel_open = not self._panel_open

    # ── meds drag-drop (called from player with inventory reference) ── #

    def handle_event(self, event, inventory_ui):
        """
        Call this each frame to support dragging a medicine item from the inventory
        onto a limb bar in the health panel. Pass the InventoryUI instance.
        Only active when the health panel is open.
        """
        if not self._panel_open:
            return

        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if user clicked on medicine item in inventory
            if inventory_ui.open:
                for slot in inventory_ui.inv_slots:
                    if (slot.item and slot.item.item_type == "bandage"
                            and slot.rect.collidepoint(mx, my)):
                        self._dragging_meds= True
                        self._drag_item        = slot.item
                        self._drag_src_slot    = slot
                        slot.item = None          # lift from slot
                        break
                    elif (slot.item and slot.item.item_type == "medkit"
                            and slot.rect.collidepoint(mx, my)):
                        self._dragging_meds = True
                        self._drag_item        = slot.item
                        self._drag_src_slot    = slot
                        slot.item = None          # lift from slot
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_meds:
                dropped = False
                if self._drag_item.item_type == "bandage":
                    for part_name, bar_rect in self._bar_rects.items():
                        if bar_rect.collidepoint(mx, my):
                            part = self.parts[part_name]
                            part.bleeding = False
                            part.heal(25)             # bandage also heals a little
                            # consume one bandage
                            self._drag_item.count -= 1
                            if self._drag_item.count <= 0:
                                self._drag_src_slot.item = None
                            else:
                                self._drag_src_slot.item = self._drag_item
                            dropped = True
                            break
                elif self._drag_item.item_type == "medkit":
                    for part_name, bar_rect in self._bar_rects.items():
                        if bar_rect.collidepoint(mx, my):
                            part = self.parts[part_name]
                            #part.bleeding  = False
                            part.heal(80)             # medkit heals a lot
                            # consume one medkit
                            self._drag_item.count -= 1
                            if self._drag_item.count <= 0:
                                self._drag_src_slot.item = None
                            else:
                                self._drag_src_slot.item = self._drag_item
                            dropped = True
                            break
                if not dropped:
                    # return item to slot
                    if self._drag_src_slot.item is None:
                        self._drag_src_slot.item = self._drag_item
                    else:
                        # slot was taken in the meantime — find another
                        for slot in inventory_ui.inv_slots:
                            if slot.item is None:
                                slot.item = self._drag_item
                                break
                self._dragging_meds = False
                self._drag_item        = None
                self._drag_src_slot    = None

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging_meds:
                self._drag_pos = (mx, my)

    # ── draw ───────────────────────────────────────────────────────────── #

    def draw(self, screen):
        self._draw_compact(screen)
        self._draw_moodles(screen)
        if self._panel_open:
            self._draw_full_panel(screen)
        # Draw dragged medicine item ghost on top of everything
        if self._dragging_meds and self._drag_item:
            self._draw_drag_ghost(screen)

    def _draw_compact(self, screen):
        x0   = 20
        y0   = 100
        bw   = 120
        bh   = 10
        gap  = 16
        font = _font(18, True)

        for i, (name, part) in enumerate(self.parts.items()):
            y = y0 + i * gap
            pygame.draw.rect(screen, (50, 0, 0), (x0, y, bw, bh))
            fw = int(bw * part.ratio)
            if fw > 0:
                pygame.draw.rect(screen, _hp_color(part.ratio), (x0, y, fw, bh))
            pygame.draw.rect(screen, C_BORDER, (x0, y, bw, bh), 1)

            weight_pct = int(PART_HIT_WEIGHT.get(name, 0) * 100)
            flags = ""
            if part.bleeding: flags += " ♥"
            # if part.fractured: flags += " ✕"   # unused
            label = font.render(f"{name}{flags} [{weight_pct}%]", True,
                                C_BLEED if part.bleeding else C_TEXT)
            screen.blit(label, (x0 + bw + 4, y - 1))

        hint = _font(18).render("[H] Health", True, C_DIM)
        screen.blit(hint, (x0, y0 + len(self.parts) * gap + 2))

    def _draw_moodles(self, screen):
        moodles = []
        if self.in_pain:  moodles.append(("Pain",     (220, 80,  80)))
        if self.injured:  moodles.append(("Injured",  (220, 130, 40)))
        if self.bleeding: moodles.append(("Bleeding", (200, 30,  30)))
        # if self.sick:     moodles.append(("Sick",     (100, 200, 80)))   # unused
        # if self.tired:    moodles.append(("Tired",    (120, 120, 200)))  # unused

        mw, mh = 90, 28
        mx = settings.WIDTH - mw - 10
        my = 10
        for text, color in moodles:
            surf = pygame.Surface((mw, mh), pygame.SRCALPHA)
            surf.fill((*color[:3], 180))
            screen.blit(surf, (mx, my))
            pygame.draw.rect(screen, color, (mx, my, mw, mh), 2, border_radius=4)
            t = _font(20, True).render(text, True, (255, 255, 255))
            screen.blit(t, (mx + mw // 2 - t.get_width() // 2,
                            my + mh // 2 - t.get_height() // 2))
            my += mh + 4

    def _draw_full_panel(self, screen):
        mx, my = pygame.mouse.get_pos()

        COLS = 2
        rows = (len(PART_NAMES) + 1) // COLS
        pw   = 420
        ph   = 60 + rows * 68
        px   = settings.WIDTH  // 2 - pw // 2
        py   = settings.HEIGHT // 2 - ph // 2

        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill(C_BG)
        screen.blit(bg, (px, py))
        pygame.draw.rect(screen, C_BORDER, (px, py, pw, ph), 2, border_radius=10)

        title = _font(30, True).render("HEALTH", True, C_TEXT)
        screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 12))

        self._bar_rects.clear()

        for i, (name, part) in enumerate(self.parts.items()):
            col = i % COLS
            row = i // COLS
            ex  = px + 14 + col * (pw // COLS)
            ey  = py + 52 + row * 68

            w_pct  = int(PART_HIT_WEIGHT.get(name, 0) * 100)
            d_mult = PART_DAMAGE_MULT.get(name, 1.0)
            name_surf = _font(18, True).render(
                f"{name}  {w_pct}% hit  x{d_mult:.1f}", True, C_TEXT)
            hp_surf = _font(20).render(
                f"{int(part.hp)}/{BodyPart.MAX_HP}", True, _hp_color(part.ratio))
            screen.blit(name_surf, (ex, ey))
            screen.blit(hp_surf,   (ex + 160, ey + 2))

            bw, bh = 160, 14
            bar_rect = pygame.Rect(ex, ey + 24, bw, bh)
            self._bar_rects[name] = bar_rect

            # Glow if dragging medicine item over this bar
            if self._dragging_meds and bar_rect.collidepoint(mx, my):
                glow_surf = pygame.Surface((bw + 8, bh + 8), pygame.SRCALPHA)
                glow_surf.fill(C_MEDS_GLOW)
                screen.blit(glow_surf, (bar_rect.x - 4, bar_rect.y - 4))

            pygame.draw.rect(screen, (50, 0, 0), bar_rect)
            fw = int(bw * part.ratio)
            if fw > 0:
                pygame.draw.rect(screen, _hp_color(part.ratio), (ex, ey + 24, fw, bh))
            pygame.draw.rect(screen, C_BORDER, bar_rect, 1)

            flags = []
            if part.bleeding: flags.append(("Bleeding", C_BLEED))
            # if part.fractured: flags.append(("Fracture", C_FRAC))   # unused
            fx = ex
            for ftxt, fcol in flags:
                fs = _font(18).render(ftxt, True, fcol)
                screen.blit(fs, (fx, ey + 42))
                fx += fs.get_width() + 8

        hint = _font(20).render("[H] Close", True, C_DIM)
        screen.blit(hint, (px + pw // 2 - hint.get_width() // 2, py + ph - 24))

    def _draw_drag_ghost(self, screen):
        mx, my = pygame.mouse.get_pos()
        size = 48
        if self._drag_item and self._drag_item.image:
            img = pygame.transform.scale(self._drag_item.image, (size, size))
            img.set_alpha(200)
            screen.blit(img, (mx - size // 2, my - size // 2))
        else:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            surf.fill((230, 230, 230, 180))
            screen.blit(surf, (mx - size // 2, my - size // 2))
