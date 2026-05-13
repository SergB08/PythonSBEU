import pygame
import settings

class Button:
    def __init__(self, x, y, w, h, text, font,
                 tex_idle, tex_hover, tex_click):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.tex_idle  = pygame.transform.scale(tex_idle,  (w, h))
        self.tex_hover = pygame.transform.scale(tex_hover, (w, h))
        self.tex_click = pygame.transform.scale(tex_click, (w, h))
        self.state = "idle"   # idle | hover | click

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)

        if hovered:
            self.state = "hover"
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.state = "click"
                    return True   # fire immediately on press
        else:
            self.state = "idle"
            
        return False

    def draw(self, screen):
        tex = {"idle": self.tex_idle,
               "hover": self.tex_hover,
               "click": self.tex_click}[self.state]
        screen.blit(tex, self.rect.topleft)

        label = self.font.render(self.text, True, (255, 255, 255))
        lx = self.rect.centerx - label.get_width() // 2
        ly = self.rect.centery - label.get_height() // 2
        screen.blit(label, (lx, ly))


class Menu:
    def __init__(self, tex_idle, tex_hover, tex_click):
        # ── font ──────────────────────────────────────────────
        self.font =  pygame.font.SysFont(None, 30, bold=True)#pygame.font.Font("fonts/1.ttf", 48)

        # ── background ────────────────────────────────────────
        # bg_image = pygame.image.load("images/menu_bg.png").convert()
        # self.bg = pygame.transform.scale(bg_image,
        #                                  (settings.WIDTH, settings.HEIGHT))
        self.bg_color = (20, 20, 30)   # placeholder solid color

        # ── buttons ───────────────────────────────────────────
        bw, bh = 320, 80
        cx = settings.WIDTH // 2 - bw // 2
        gap = 120

        start_y = settings.HEIGHT // 2 - gap

        self.buttons = {
            "play":     Button(cx, start_y,          bw, bh, "PLAY",     self.font, tex_idle, tex_hover, tex_click),
            "settings": Button(cx, start_y + gap,    bw, bh, "SETTINGS", self.font, tex_idle, tex_hover, tex_click),
            "exit":     Button(cx, start_y + gap * 2,bw, bh, "EXIT",     self.font, tex_idle, tex_hover, tex_click),
        }

    def run(self, screen, events):
        """Returns 'play' | 'settings' | 'exit' | None."""
        # background
        # screen.blit(self.bg, (0, 0))
        screen.fill(self.bg_color)

        for name, btn in self.buttons.items():
            if btn.update(events):
                return name
            btn.draw(screen)

        return None