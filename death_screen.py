import pygame
import settings
from main_menu import Button
from assets import load_menu_textures
import assets


class DeathScreen:
    def __init__(self):  
        tex_idle, tex_hover, tex_click = load_menu_textures()
        self.font_big = pygame.font.SysFont(None, 160, bold=True)
        self.font_btn = pygame.font.SysFont(None, 30,  bold=True)
        
        # Track if sound has been played for this instance
        self._sound_played = False

        bw, bh = 320, 80
        cx = settings.WIDTH  // 2 - bw // 2
        cy = settings.HEIGHT // 2 + 60

        self.buttons = {
            "restart": Button(cx, cy,       bw, bh, "RESTART",   self.font_btn, tex_idle, tex_hover, tex_click),
            "menu":    Button(cx, cy + 120, bw, bh, "MAIN MENU", self.font_btn, tex_idle, tex_hover, tex_click),
        }

    # def _play_death_sound(self):
    #     """Play death sound with proper channel management."""
    #     try:
    #         sound = pygame.mixer.Sound(assets.PlayerDeath)
    #         sound.set_volume(settings.VOLUME)
            
    #         # Find a free channel or use the first one
    #         channel = pygame.mixer.find_channel()
    #         if channel is None:
    #             # All channels busy, use channel 0 and stop its current sound
    #             channel = pygame.mixer.Channel(0)
    #             channel.stop()
            
    #         channel.play(sound)
    #     except Exception as e:
    #         print(f"Could not play death sound: {e}")

    def run(self, screen, events):
        # Play death sound only once when the screen first appears
        if not self._sound_played:
            #self._play_death_sound()
            self._sound_played = True
        
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        title = self.font_big.render("YOU DIED", True, (200, 0, 0))
        screen.blit(title, (settings.WIDTH  // 2 - title.get_width()  // 2,
                            settings.HEIGHT // 2 - 180))

        for name, btn in self.buttons.items():
            if btn.update(events):
                return name
            btn.draw(screen)
        return None