import pygame
import settings
from assets import load_menu_textures
from main_menu import Button


class Slider:
    def __init__(self, x, y, w, h, initial=1.0):
        self.rect     = pygame.Rect(x, y, w, h)
        self.value    = initial
        self.dragging = False
        self.font     = pygame.font.SysFont(None, 30, bold=True)

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.rect.collidepoint(mx, my):
                    self.dragging = True
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.dragging = False
        if self.dragging:
            self.value = max(0.0, min(1.0,
                (mx - self.rect.x) / self.rect.width))

    def draw(self, screen):
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=6)
        fill_w = int(self.rect.width * self.value)
        if fill_w > 0:
            pygame.draw.rect(screen, (180, 60, 60),
                             (self.rect.x, self.rect.y, fill_w, self.rect.height),
                             border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=6)
        hx = self.rect.x + int(self.rect.width * self.value)
        hy = self.rect.centery
        pygame.draw.circle(screen, (255, 255, 255), (hx, hy), 12)
        pygame.draw.circle(screen, (150, 150, 150), (hx, hy), 12, 2)
        pct = self.font.render(f"{int(self.value * 100)}%", True, (255, 255, 255))
        screen.blit(pct, (self.rect.right + 20,
                          self.rect.centery - pct.get_height() // 2))


class OptionRow:
    def __init__(self, label, options, current_index, x, y, btn_w, btn_h,
                 font, tex_idle, tex_hover, tex_click):
        self.label      = label
        self.options    = options
        self.selected   = current_index
        self.label_font = pygame.font.SysFont(None, 36, bold=True)
        self.x, self.y  = x, y

        gap = btn_w + 20
        self.buttons = [
            Button(x + i * gap, y, btn_w, btn_h, str(opt),
                   font, tex_idle, tex_hover, tex_click)
            for i, opt in enumerate(options)
        ]

    def update(self, events):
        for i, btn in enumerate(self.buttons):
            if btn.update(events):
                self.selected = i

    def draw(self, screen):
        lbl = self.label_font.render(self.label, True, (200, 200, 200))
        screen.blit(lbl, (self.x, self.y - 40))
        for i, btn in enumerate(self.buttons):
            btn.draw(screen)
            if i == self.selected:
                pygame.draw.rect(screen, (255, 200, 50), btn.rect, 3, border_radius=4)


class SettingsMenu:
    WINDOW_OPTIONS = ["Windowed", "Fullscreen", "Borderless"]
    FPS_OPTIONS    = [30, 60, 144]
    RES_OPTIONS    = ["1280x720", "1920x1080", "2560x1440"]

    def __init__(self):
        self._textures = load_menu_textures()
        self.font      = pygame.font.SysFont(None, 30, bold=True)
        self.font_big  = pygame.font.SysFont(None, 72, bold=True)
        self.bg_color  = (20, 20, 30)
        self._build()

    def _build(self):
        """Rebuild all widget positions from current settings.WIDTH/HEIGHT."""
        tex_idle, tex_hover, tex_click = self._textures

        cx  = settings.WIDTH  // 2
        col = cx - 300
        bw, bh = 180, 60

        top_margin = settings.HEIGHT // 8
        row_height = (settings.HEIGHT - top_margin - 100) // 4

        # Read current selections from settings
        fps_sel = self.FPS_OPTIONS.index(settings.FPS) \
                  if settings.FPS in self.FPS_OPTIONS else 1
        current_res = f"{settings.WIDTH}x{settings.HEIGHT}"
        res_sel = self.RES_OPTIONS.index(current_res) \
                  if current_res in self.RES_OPTIONS else 0

        self.volume_slider = Slider(col, top_margin, 400, 20,
                                    initial=settings.VOLUME)

        self.row_window = OptionRow(
            "Window Mode", self.WINDOW_OPTIONS, settings.WINDOW_MODE,
            col, top_margin + row_height, bw, bh,
            self.font, tex_idle, tex_hover, tex_click)

        self.row_fps = OptionRow(
            "Max FPS", self.FPS_OPTIONS, fps_sel,
            col, top_margin + row_height * 2, bw, bh,
            self.font, tex_idle, tex_hover, tex_click)

        self.row_res = OptionRow(
            "Resolution", self.RES_OPTIONS, res_sel,
            col, top_margin + row_height * 3, bw, bh,
            self.font, tex_idle, tex_hover, tex_click)

        self.btn_back = Button(cx - 160, settings.HEIGHT - 100, 320, 70, "BACK",
                               self.font, tex_idle, tex_hover, tex_click)

    def _apply(self):
        """Save widget state to settings, apply everything, then rebuild."""
        # Save to settings module
        settings.VOLUME      = self.volume_slider.value
        settings.WINDOW_MODE = self.row_window.selected
        settings.FPS         = self.FPS_OPTIONS[self.row_fps.selected]

        res_str = self.RES_OPTIONS[self.row_res.selected]
        w, h    = map(int, res_str.split("x"))
        settings.WIDTH  = w
        settings.HEIGHT = h

        # Apply audio
        pygame.mixer.music.set_volume(settings.VOLUME)
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(settings.VOLUME)

        # Apply display mode
        if settings.WINDOW_MODE == 0:
            pygame.display.set_mode((w, h))
        elif settings.WINDOW_MODE == 1:
            pygame.display.set_mode((w, h), pygame.FULLSCREEN)
        elif settings.WINDOW_MODE == 2:
            pygame.display.set_mode((w, h), pygame.NOFRAME)

        # Rebuild layout for the new resolution
        self._build()

    def run(self, screen, events):
        """Returns 'back' when done, else None."""
        screen.fill(self.bg_color)

        title = self.font_big.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, (settings.WIDTH  // 2 - title.get_width()  // 2, 80))

        vol_lbl = self.font.render("Volume", True, (200, 200, 200))
        screen.blit(vol_lbl, (settings.WIDTH // 2 - 300,
                               self.volume_slider.rect.y - 40))

        self.volume_slider.update(events)
        self.volume_slider.draw(screen)

        for row in (self.row_window, self.row_fps, self.row_res):
            row.update(events)
            row.draw(screen)

        if self.btn_back.update(events):
            self._apply()
            return "back"
        self.btn_back.draw(screen)

        return None