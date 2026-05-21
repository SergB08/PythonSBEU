import pygame
import settings
from main_menu import Button
from assets import load_menu_textures
import assets


class DeathScreen:
    def __init__(self):
        tex_idle, tex_hover, tex_click = load_menu_textures()
        self.font_big = pygame.font.SysFont(None, 160, bold=True)  # шрифт для заголовку
        self.font_btn = pygame.font.SysFont(None, 30,  bold=True)  # шрифт для кнопок
        
        # відстежує чи був вже зіграний звук для цього екрану
        self._sound_played = False

        # розміщення кнопок по центру екрану
        bw, bh = 320, 80
        cx = settings.WIDTH  // 2 - bw // 2
        cy = settings.HEIGHT // 2 + 60

        self.buttons = {
            "restart": Button(cx, cy,       bw, bh, "RESTART",   self.font_btn, tex_idle, tex_hover, tex_click),
            "menu":    Button(cx, cy + 120, bw, bh, "MAIN MENU", self.font_btn, tex_idle, tex_hover, tex_click),
        }

    def run(self, screen, events):
        # відтворює звук смерті лише один раз при появі екрану
        if not self._sound_played:
            self._sound_played = True
        
        # напівпрозорий темний оверлей поверх гри
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        # заголовок "YOU DIED" по центру
        title = self.font_big.render("YOU DIED", True, (200, 0, 0))
        screen.blit(title, (settings.WIDTH  // 2 - title.get_width()  // 2,
                            settings.HEIGHT // 2 - 180))

        # оновлює та малює кнопки, повертає назву натиснутої
        for name, btn in self.buttons.items():
            if btn.update(events):
                return name
            btn.draw(screen)
        return None