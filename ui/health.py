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
C_FRAC   = (180, 160, 100)

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
    """Pick a body part using PART_HIT_WEIGHT distribution."""
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
        self.fractured = False

    @property
    def alive(self):
        return self.hp > 0

    def take_damage(self, amount: float):
        """Apply final (already-multiplied) damage directly."""
        self.hp = max(0.0, self.hp - amount)

    def heal(self, amount: float):
        self.hp = min(float(self.MAX_HP), self.hp + amount)

    def update(self, dt: float):
        if self.bleeding and self.hp > 0:
            self.hp = max(0.0, self.hp - 2.0 * dt)

    @property
    def ratio(self):
        return self.hp / self.MAX_HP


# ── Full health model ──────────────────────────────────────────────────────
class BodyHealth:
    def __init__(self):
        self.parts: dict[str, BodyPart] = {n: BodyPart(n) for n in PART_NAMES}
        self.alive = True
        self.sick   = False
        self.tired  = False
        self._panel_open = False

    # ── damage ─────────────────────────────────────────────────────────── #

    def take_damage(self, amount: float, part_name: str = "Torso"):
        """
        Hit a specific part. Applies that part's damage multiplier.
        Always deals at least 1 damage so hits are never silent.
        """
        if not self.alive:
            return
        part  = self.parts.get(part_name, self.parts["Torso"])
        mult  = PART_DAMAGE_MULT.get(part_name, 1.0)
        final = max(1.0, amount * mult)
        part.take_damage(final)
        if final >= 8:
            part.bleeding = True
        self._check_death()

    def take_damage_any(self, amount: float):
        """
        Random hit using PART_HIT_WEIGHT — selects one body part,
        applies its multiplier, guaranteed to deal damage every call.
        """
        if not self.alive:
            return
        part_name = _random_part()
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
            part.fractured = False
        self.alive = True
        self.sick   = False
        self.tired  = False

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
        for part in self.parts.values():
            part.update(dt)
        self._check_death()

    def toggle_panel(self):
        self._panel_open = not self._panel_open

    # ── draw ───────────────────────────────────────────────────────────── #

    def draw(self, screen):
        self._draw_compact(screen)
        self._draw_moodles(screen)
        if self._panel_open:
            self._draw_full_panel(screen)

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
            if part.bleeding:  flags += " ♥"
            if part.fractured: flags += " ✕"
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
        if self.sick:     moodles.append(("Sick",     (100, 200, 80)))
        if self.tired:    moodles.append(("Tired",    (120, 120, 200)))

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
            pygame.draw.rect(screen, (50, 0, 0), (ex, ey + 24, bw, bh))
            fw = int(bw * part.ratio)
            if fw > 0:
                pygame.draw.rect(screen, _hp_color(part.ratio), (ex, ey + 24, fw, bh))
            pygame.draw.rect(screen, C_BORDER, (ex, ey + 24, bw, bh), 1)

            flags = []
            if part.bleeding:  flags.append(("Bleeding", C_BLEED))
            if part.fractured: flags.append(("Fracture", C_FRAC))
            fx = ex
            for ftxt, fcol in flags:
                fs = _font(18).render(ftxt, True, fcol)
                screen.blit(fs, (fx, ey + 42))
                fx += fs.get_width() + 8

        hint = _font(20).render("[H] Close", True, C_DIM)
        screen.blit(hint, (px + pw // 2 - hint.get_width() // 2, py + ph - 24))