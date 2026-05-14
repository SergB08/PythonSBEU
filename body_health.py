import pygame
import random

# ─────────────────────────────────────────────────────────────────────────────
#  BODY PART HEALTH
#  Each part has its own HP pool and hit-chance weight.
#  Critical parts (head) do bonus damage when hit.
# ─────────────────────────────────────────────────────────────────────────────

PARTS = [
    # name,    max_hp, hit_weight, damage_multiplier
    ("Head",   30,     0.10,       2.0),
    ("Chest",  60,     0.35,       1.0),
    ("Arms",   40,     0.20,       0.8),
    ("Legs",   40,     0.25,       0.8),
    ("Torso",  50,     0.10,       1.0),   # gut / lower abdomen
]

PART_COLORS = {
    "Head":  (220, 80,  80),
    "Chest": (80,  160, 220),
    "Arms":  (80,  200, 120),
    "Legs":  (200, 160, 60),
    "Torso": (160, 100, 200),
}

class BodyHealth:
    """Tracks HP per body-part; replaces the old single hp / MAX_HP."""

    def __init__(self):
        self.parts = {
            name: {"hp": max_hp, "max": max_hp,
                   "weight": w, "dmg_mult": mult}
            for name, max_hp, w, mult in PARTS
        }
        self._font      = None
        self._font_lbl  = None

    # ── derived totals ─────────────────────────────────────────────────── #

    @property
    def hp(self):
        return sum(v["hp"] for v in self.parts.values())

    @property
    def max_hp(self):
        return sum(v["max"] for v in self.parts.values())

    @property
    def alive(self):
        # Dead if head HP = 0 OR total HP = 0
        return self.parts["Head"]["hp"] > 0 and self.hp > 0

    # ── taking damage ──────────────────────────────────────────────────── #

    def take_damage(self, base_amount, force_part=None):
        """
        Distribute damage to a random body part (weighted).
        Returns (part_name, actual_damage_dealt).
        """
        if force_part and force_part in self.parts:
            part_name = force_part
        else:
            names   = list(self.parts.keys())
            weights = [self.parts[n]["weight"] for n in names]
            part_name = random.choices(names, weights=weights, k=1)[0]

        part   = self.parts[part_name]
        actual = int(base_amount * part["dmg_mult"])
        part["hp"] = max(0, part["hp"] - actual)
        return part_name, actual

    def heal(self, amount, part_name=None):
        """Heal a part (or the most-damaged part if none specified)."""
        if part_name and part_name in self.parts:
            p = self.parts[part_name]
            p["hp"] = min(p["max"], p["hp"] + amount)
        else:
            # heal the most-damaged part proportionally
            worst = min(self.parts.items(),
                        key=lambda kv: kv[1]["hp"] / kv[1]["max"])
            p = worst[1]
            p["hp"] = min(p["max"], p["hp"] + amount)

    def heal_all(self, amount):
        for p in self.parts.values():
            p["hp"] = min(p["max"], p["hp"] + amount)

    # ── HUD drawing ────────────────────────────────────────────────────── #

    def draw_hud(self, screen):
        if self._font is None:
            self._font     = pygame.font.SysFont(None, 18, bold=True)
            self._font_lbl = pygame.font.SysFont(None, 20, bold=True)

        PAD    = 14
        BAR_W  = 120
        BAR_H  = 14
        ROW_H  = 28
        LABEL_W = 48

        panel_h = len(self.parts) * ROW_H + 28
        panel_w = LABEL_W + BAR_W + 64
        panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 10, 20, 190))
        screen.blit(panel, (PAD - 6, PAD - 6))
        pygame.draw.rect(screen, (80, 80, 100),
                         pygame.Rect(PAD - 6, PAD - 6, panel_w, panel_h), 1,
                         border_radius=4)

        title = self._font_lbl.render("HEALTH", True, (200, 200, 220))
        screen.blit(title, (PAD, PAD))

        for i, (name, data) in enumerate(self.parts.items()):
            y    = PAD + 22 + i * ROW_H
            ratio = max(0.0, data["hp"] / data["max"])
            fill_col = PART_COLORS.get(name, (180, 180, 180))
            dark_col = tuple(max(0, c // 3) for c in fill_col)

            # label
            lbl = self._font.render(name, True, (200, 200, 200))
            screen.blit(lbl, (PAD, y + BAR_H // 2 - lbl.get_height() // 2))

            bx = PAD + LABEL_W
            # background
            pygame.draw.rect(screen, (50, 10, 10), (bx, y, BAR_W, BAR_H), border_radius=3)
            # fill
            fw = int(BAR_W * ratio)
            if fw > 0:
                pygame.draw.rect(screen, fill_col, (bx, y, fw, BAR_H), border_radius=3)
            # border
            pygame.draw.rect(screen, (160, 160, 160), (bx, y, BAR_W, BAR_H), 1, border_radius=3)

            # percentage
            pct = self._font.render(f"{int(ratio * 100)}%", True, (230, 230, 230))
            screen.blit(pct, (bx + BAR_W + 6, y + BAR_H // 2 - pct.get_height() // 2))