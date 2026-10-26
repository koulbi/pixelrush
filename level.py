"""Levels, platforms, spikes, coins, checkpoints and the finish arch."""
import math
import random

import pygame

import fx
from config import FONT_BOLD, HEIGHT, WHITE, WIDTH

THEMES = {
    "meadow": {
        "sky_top": (154, 210, 232),
        "sky_bottom": (255, 238, 205),
        "sun": (255, 204, 96),
        "sun_glow": (255, 226, 150),
        "skyline": (128, 178, 136),
        "skyline_light": (98, 154, 108),
        "window": (255, 250, 240),
        "platform": (176, 120, 76),
        "platform_light": (200, 146, 96),
        "edge": (104, 160, 92),
        "accent": (214, 92, 88),
    },
    "coast": {
        "sky_top": (140, 200, 222),
        "sky_bottom": (255, 232, 198),
        "sun": (255, 190, 92),
        "sun_glow": (255, 220, 140),
        "skyline": (108, 166, 168),
        "skyline_light": (78, 136, 142),
        "window": (255, 250, 240),
        "platform": (172, 120, 82),
        "platform_light": (198, 146, 100),
        "edge": (76, 146, 142),
        "accent": (224, 112, 86),
    },
    "canyon": {
        "sky_top": (255, 210, 160),
        "sky_bottom": (255, 244, 218),
        "sun": (255, 176, 78),
        "sun_glow": (255, 214, 130),
        "skyline": (198, 126, 96),
        "skyline_light": (166, 94, 70),
        "window": (255, 250, 240),
        "platform": (164, 102, 62),
        "platform_light": (192, 132, 82),
        "edge": (198, 128, 68),
        "accent": (190, 78, 64),
    },
}


def coin_row(x, y, count, step=42):
    return [(x + i * step, y) for i in range(count)]


def coin_arc(x, y, count, step=44, rise=64):
    return [
        (x + i * step, y - math.sin((i + 0.5) / count * math.pi) * rise)
        for i in range(count)
    ]


LEVELS = [
    {
        "name": "SUNNY START",
        "subtitle": "Warm up: spikes, coins and your first portal",
        "theme": "meadow",
        "seed": 3,
        "width": 3600,
        "spawn": (80, 566),
        "goal": (3430, 620),
        "ground": [
            (0, 620, 700, 130),
            (860, 620, 420, 130),
            (1440, 620, 320, 130),
            (1990, 620, 380, 130),
            (2490, 620, 360, 130),
            (2990, 620, 610, 130),
        ],
        "platforms": [
            (250, 500, 130, 18), (430, 400, 130, 18), (650, 320, 120, 18),
            (980, 510, 120, 18), (1150, 420, 120, 18), (1300, 340, 110, 18),
            (1560, 500, 120, 18), (1720, 400, 120, 18),
            (2070, 500, 130, 18), (2250, 410, 120, 18),
            (2600, 510, 120, 18), (2780, 420, 120, 18),
            (3100, 480, 130, 18), (3300, 380, 120, 18),
        ],
        "moving": [
            (700, 545, 120, 18, 0, -120, 1.6, 0.0),
            (1810, 520, 130, 18, 150, 0, 2.0, 0.0),
            (2830, 500, 120, 18, 120, 0, 2.4, 1.0),
        ],
        "spikes": [
            (430, 620, 70, "up"),
            (1000, 620, 60, "up"),
            (1600, 620, 80, "up"),
            (2200, 620, 70, "up"),
            (2650, 620, 60, "up"),
            (3140, 620, 70, "up"),
        ],
        "coins": (
            coin_arc(140, 555, 6, 46, 80)
            + coin_row(270, 455, 3)
            + coin_row(455, 355, 3)
            + coin_row(675, 275, 2)
            + coin_arc(715, 490, 4, 45, 50)
            + coin_row(1000, 465, 2)
            + coin_row(1170, 375, 2)
            + coin_row(1320, 295, 2)
            + coin_row(1580, 455, 2)
            + coin_row(1740, 355, 2)
            + coin_arc(1830, 470, 4, 45, 40)
            + coin_row(2090, 455, 2)
            + coin_row(2270, 365, 2)
            + coin_row(2620, 465, 2)
            + coin_row(2800, 375, 2)
            + coin_row(3120, 435, 2)
            + coin_row(3320, 335, 2)
            + coin_arc(3220, 560, 4, 42, 40)
        ),
        "checkpoints": [(1460, 620), (2520, 620)],
    },
    {
        "name": "ROOFTOP RUN",
        "subtitle": "Higher ground: ceiling spikes and moving lifts",
        "theme": "coast",
        "seed": 17,
        "width": 3950,
        "spawn": (80, 566),
        "goal": (3780, 620),
        "ground": [
            (0, 620, 520, 130),
            (720, 620, 260, 130),
            (1200, 540, 220, 190),
            (1620, 620, 220, 130),
            (2060, 500, 240, 220),
            (2500, 620, 240, 130),
            (2940, 560, 300, 160),
            (3420, 620, 480, 130),
        ],
        "platforms": [
            (300, 480, 120, 18), (500, 380, 120, 18),
            (760, 480, 110, 18), (900, 390, 110, 18),
            (1250, 430, 110, 18), (1450, 350, 110, 18),
            (1760, 500, 110, 18), (1950, 390, 100, 18),
            (2180, 350, 120, 18), (2360, 440, 110, 18),
            (2640, 500, 110, 18), (2820, 400, 110, 18),
            (3090, 440, 120, 18), (3280, 340, 110, 18),
            (3520, 480, 120, 18),
            (600, 280, 120, 18), (2580, 310, 120, 18),
        ],
        "moving": [
            (520, 560, 120, 18, 0, -120, 1.8, 0.0),
            (1010, 520, 120, 18, 140, 0, 1.7, 0.6),
            (1860, 560, 120, 18, 0, -130, 1.5, 0.0),
            (2700, 530, 120, 18, 130, 0, 2.0, 0.8),
            (3200, 560, 110, 18, 0, -110, 2.2, 0.0),
        ],
        "spikes": [
            (360, 620, 70, "up"),
            (800, 620, 60, "up"),
            (1300, 540, 70, "up"),
            (1740, 620, 60, "up"),
            (2150, 500, 70, "up"),
            (2660, 620, 60, "up"),
            (3080, 560, 80, "up"),
            (3600, 620, 80, "up"),
            (620, 298, 80, "down"),
            (2600, 328, 80, "down"),
        ],
        "coins": (
            coin_arc(120, 555, 6, 46, 80)
            + coin_row(320, 435, 2)
            + coin_row(520, 335, 2)
            + coin_arc(560, 500, 4, 45, 50)
            + coin_row(780, 435, 2)
            + coin_row(920, 345, 2)
            + coin_row(1270, 385, 2)
            + coin_row(1470, 305, 2)
            + coin_row(1780, 455, 2)
            + coin_row(1970, 345, 2)
            + coin_row(2200, 305, 2)
            + coin_row(2380, 395, 2)
            + coin_row(2660, 455, 2)
            + coin_row(2840, 355, 2)
            + coin_row(3110, 395, 2)
            + coin_row(3300, 295, 2)
            + coin_row(3540, 435, 2)
            + coin_arc(3640, 560, 5, 44, 50)
        ),
        "checkpoints": [(1650, 620), (2550, 620), (3480, 620)],
    },
    {
        "name": "CANYON CORE",
        "subtitle": "The final dash across sun-baked platforms",
        "theme": "canyon",
        "seed": 31,
        "width": 4250,
        "spawn": (80, 566),
        "goal": (4080, 620),
        "ground": [
            (0, 620, 420, 130),
            (620, 560, 260, 160),
            (1080, 620, 240, 130),
            (1480, 560, 200, 160),
            (1840, 620, 220, 130),
            (2240, 540, 220, 180),
            (2620, 620, 200, 130),
            (3020, 560, 220, 160),
            (3420, 620, 240, 130),
            (3820, 620, 380, 130),
        ],
        "platforms": [
            (180, 480, 120, 18),
            (680, 460, 120, 18),
            (1150, 480, 110, 18),
            (1540, 440, 110, 18),
            (1900, 490, 120, 18),
            (2310, 430, 110, 18),
            (2700, 490, 110, 18),
            (3100, 440, 110, 18),
            (3500, 490, 110, 18),
            (3900, 440, 120, 18),
            (370, 300, 120, 18),
            (2500, 320, 120, 18),
        ],
        "moving": [
            (430, 520, 110, 18, 100, 0, 2.6, 0.0),
            (900, 520, 110, 18, 0, -130, 2.0, 0.4),
            (1330, 500, 110, 18, 100, 0, 2.8, 0.0),
            (2070, 500, 110, 18, 0, -120, 2.2, 0.9),
            (2470, 520, 110, 18, 120, 0, 2.6, 0.0),
            (2840, 520, 110, 18, 0, -130, 2.4, 0.2),
            (3250, 500, 110, 18, 110, 0, 3.0, 0.0),
            (3670, 520, 110, 18, 0, -120, 2.6, 0.7),
        ],
        "spikes": [
            (180, 620, 70, "up"),
            (720, 560, 60, "up"),
            (1120, 620, 80, "up"),
            (1580, 560, 60, "up"),
            (1930, 620, 70, "up"),
            (2300, 540, 80, "up"),
            (2710, 620, 60, "up"),
            (3120, 560, 80, "up"),
            (3560, 620, 60, "up"),
            (3970, 620, 70, "up"),
            (390, 318, 80, "down"),
        ],
        "coins": (
            coin_arc(100, 555, 5, 46, 80)
            + coin_row(200, 435, 2)
            + coin_row(700, 415, 2)
            + coin_arc(500, 480, 4, 40, 50)
            + coin_row(1170, 435, 2)
            + coin_row(1560, 395, 2)
            + coin_row(1920, 445, 2)
            + coin_row(2330, 385, 2)
            + coin_row(2720, 445, 2)
            + coin_row(3120, 395, 2)
            + coin_row(3520, 445, 2)
            + coin_row(3920, 395, 2)
            + coin_arc(3980, 560, 4, 44, 50)
            + coin_row(390, 255, 2)
            + coin_row(2510, 275, 2)
        ),
        "checkpoints": [(1500, 560), (2650, 620), (3450, 620)],
    },
]

_finish_font = None


def _small_font(size):
    global _finish_font
    if _finish_font is None:
        _finish_font = pygame.font.Font(FONT_BOLD, 14)
    return _finish_font


class Platform:
    one_way = False
    moving = False

    def __init__(self, x, y, w, h, one_way=False):
        self.rect = pygame.Rect(int(x), int(y), int(w), int(h))
        self.one_way = one_way
        self.delta = (0.0, 0.0)

    def update(self):
        pass


class MovingPlatform(Platform):
    moving = True

    def __init__(self, x, y, w, h, dx, dy, speed, phase=0.0):
        super().__init__(x, y, w, h, one_way=True)
        self.base_x = float(x)
        self.base_y = float(y)
        self.dx = float(dx)
        self.dy = float(dy)
        self.speed = float(speed)
        self.t = float(phase)
        nx, ny = self._position()
        self.rect.x = round(nx)
        self.rect.y = round(ny)

    def _position(self):
        # плавное движение строго от base до base+dx/dy (без колебаний назад)
        k = (1.0 - math.cos(self.t)) * 0.5
        return self.base_x + k * self.dx, self.base_y + k * self.dy

    def update(self):
        self.t += 0.018 * self.speed
        nx, ny = self._position()
        new_x, new_y = round(nx), round(ny)
        self.delta = (new_x - self.rect.x, new_y - self.rect.y)
        self.rect.x = new_x
        self.rect.y = new_y


class Spike:
    def __init__(self, x, y, width, direction="up"):
        self.x = int(x)
        self.y = int(y)
        self.w = int(width)
        self.dir = direction
        self.h = 22
        if direction == "up":
            self.hitbox = pygame.Rect(self.x + 5, self.y - 17, self.w - 10, 13)
        elif direction == "down":
            self.hitbox = pygame.Rect(self.x + 5, self.y + 4, self.w - 10, 13)
        elif direction == "left":
            self.hitbox = pygame.Rect(self.x, self.y + 5, 13, self.w - 10)
        else:
            self.hitbox = pygame.Rect(self.x + 4, self.y + 5, 13, self.w - 10)

    def draw(self, surface, offset, theme):
        ox, oy = offset
        x = self.x - ox
        y = self.y - oy
        count = max(1, round(self.w / 24))
        step = self.w / count
        dark = (92, 58, 46)
        mid = theme["accent"]
        light = fx.mix(mid, (255, 250, 240), 0.45)
        if self.dir in ("up", "down"):
            sign = -1 if self.dir == "up" else 1
            pygame.draw.rect(surface, dark, (x, y - 2, self.w, 4), border_radius=2)
            for i in range(count):
                sx = x + i * step
                tip = (sx + step / 2, y + 22 * sign)
                pygame.draw.polygon(surface, dark, [
                    (sx - 1, y), (sx + step + 1, y), (tip[0], tip[1] + sign),
                ])
                pygame.draw.polygon(surface, mid, [
                    (sx + 1, y), (sx + step - 1, y), tip,
                ])
                pygame.draw.polygon(surface, light, [
                    (sx + step * 0.22, y), (sx + step * 0.54, y),
                    (sx + step / 2, y + 13 * sign),
                ])


class Coin:
    def __init__(self, x, y):
        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.phase = random.Random(x * 13 + y * 7).random() * math.tau
        self.collected = False
        self.attracted = False

    def update(self, t):
        if self.attracted:
            return
        self.y = self.base_y + math.sin(t * 3.0 + self.phase) * 3.5

    def draw(self, surface, offset, t):
        ox, oy = offset
        x = int(self.x - ox)
        y = int(self.y - oy)
        if x < -40 or x > WIDTH + 40:
            return
        spin = abs(math.cos(t * 3.4 + self.phase))
        rx = max(2, int(10 * spin))
        pygame.draw.ellipse(surface, (120, 78, 44),
                            (x - rx - 2, y - 12, rx * 2 + 4, 26))
        pygame.draw.ellipse(surface, (236, 170, 58),
                            (x - rx - 1, y - 11, rx * 2 + 2, 24))
        pygame.draw.ellipse(surface, (250, 204, 96),
                            (x - rx, y - 10, rx * 2, 22))
        if rx > 4:
            pygame.draw.ellipse(surface, (255, 226, 140),
                                (x - rx + 2, y - 7, max(1, rx - 2), 15))
            pygame.draw.ellipse(surface, (255, 250, 220),
                                (x - rx + 3, y - 5, max(1, rx // 2), 5))
        else:
            pygame.draw.line(surface, (250, 220, 120), (x, y - 9), (x, y + 9), 2)


class Checkpoint:
    def __init__(self, x, ground_y):
        self.x = int(x)
        self.y = int(ground_y)
        self.active = False
        self.rect = pygame.Rect(self.x - 22, self.y - 76, 44, 76)
        self.respawn = (self.x - 17, self.y - 46)
        self.pulse = 0.0

    def draw(self, surface, offset, theme, t):
        ox, oy = offset
        x = self.x - ox
        y = self.y - oy
        if x < -60 or x > WIDTH + 60:
            return
        pole_color = theme["edge"] if self.active else (176, 152, 126)
        dark = (104, 74, 54)
        pygame.draw.ellipse(surface, (150, 116, 82),
                            (x - 14, y - 8, 28, 8))
        pygame.draw.circle(surface, (255, 250, 238), (x, y - 3), 9)
        pygame.draw.circle(surface, dark, (x, y - 3), 9, 2)
        pygame.draw.circle(surface, pole_color, (x, y - 3), 3)
        pygame.draw.line(surface, dark, (x, y - 8), (x, y - 64), 5)
        pygame.draw.line(surface, (216, 180, 136), (x, y - 8), (x, y - 64), 2)
        wave = math.sin(t * 4 + self.x * 0.1) * 4 if self.active else 0
        flag = [
            (x + 2, y - 62),
            (x + 34, y - 55 + wave),
            (x + 2, y - 44),
        ]
        pygame.draw.polygon(surface, pole_color, flag)
        pygame.draw.polygon(surface, dark, flag, 2)
        if self.active:
            pygame.draw.circle(surface, (255, 250, 238), (x + 14, y - 55), 3)
            for i in range(3):
                ang = t * 1.6 + i * math.tau / 3
                pygame.draw.circle(surface, theme["accent"],
                                   (int(x + 18 + math.cos(ang) * 8),
                                    int(y - 54 + math.sin(ang) * 6)), 2)


class Goal:
    def __init__(self, x, ground_y):
        self.x = int(x)
        self.y = int(ground_y)
        self.rect = pygame.Rect(self.x - 32, self.y - 124, 64, 124)
        self.phase = 0.0

    def draw(self, surface, offset, theme, t):
        ox, oy = offset
        x = self.x - ox
        y = self.y - oy
        if x < -140 or x > WIDTH + 140:
            return
        accent = theme["edge"]
        accent2 = theme["accent"]
        dark = (104, 74, 54)
        pygame.draw.ellipse(surface, (150, 116, 82), (x - 52, y - 8, 104, 12))

        arch = pygame.Rect(x - 44, y - 136, 88, 96)
        for side in (-1, 1):
            px = x + side * 38
            pygame.draw.rect(surface, dark, (px - 7, y - 104, 14, 106), border_radius=6)
            pygame.draw.rect(surface, accent, (px - 5, y - 102, 10, 104), border_radius=5)
            pygame.draw.rect(surface, fx.mix(accent, (255, 250, 238), 0.25),
                             (px - 3, y - 98, 3, 94), border_radius=2)
        pygame.draw.arc(surface, dark, arch, 0.05, math.pi - 0.05, 16)
        pygame.draw.arc(surface, accent2, arch, 0.05, math.pi - 0.05, 11)

        # little flowers on the arch
        for i in range(5):
            ang = math.pi * (i + 0.5) / 5
            px = x + math.cos(ang) * 44
            py = y - 88 - math.sin(ang) * 48
            for k in range(5):
                a = k * math.tau / 5
                pygame.draw.circle(surface, (255, 238, 196),
                                   (int(px + math.cos(a) * 5), int(py + math.sin(a) * 5)), 4)
            pygame.draw.circle(surface, (245, 190, 72), (int(px), int(py)), 3)

        # hanging banner
        banner = [(x - 22, y - 92), (x + 22, y - 92), (x + 22, y - 62),
                  (x, y - 50), (x - 22, y - 62)]
        pygame.draw.polygon(surface, accent2, banner)
        pygame.draw.polygon(surface, dark, banner, 2)
        pygame.draw.circle(surface, (255, 250, 238), (x, y - 76), 3)

        label = _small_font(14).render("FINISH", True, (62, 48, 40))
        sign = pygame.Rect(x - label.get_width() // 2 - 9, y - 168,
                           label.get_width() + 18, 24)
        pygame.draw.rect(surface, (255, 250, 238), sign, border_radius=7)
        pygame.draw.rect(surface, dark, sign, 2, border_radius=7)
        surface.blit(label, (x - label.get_width() // 2, y - 162))
        pygame.draw.rect(surface, accent2, (x - 34, y - 3, 68, 4), border_radius=2)


class Level:
    def __init__(self, data, index):
        self.data = data
        self.index = index
        self.name = data["name"]
        self.subtitle = data["subtitle"]
        self.theme = THEMES[data["theme"]]
        self.width = data["width"]
        self.height = HEIGHT
        self.spawn = data["spawn"]
        self.solids = []
        self.oneways = []
        self.platforms = []
        for x, y, w, h in data["ground"]:
            platform = Platform(x, y, w, h)
            self.solids.append(platform)
            self.platforms.append(platform)
        for x, y, w, h in data["platforms"]:
            platform = Platform(x, y, w, h, one_way=True)
            self.oneways.append(platform)
            self.platforms.append(platform)
        self.moving = []
        for args in data["moving"]:
            platform = MovingPlatform(*args)
            self.moving.append(platform)
            self.oneways.append(platform)
            self.platforms.append(platform)

        self.spikes = [Spike(*args) for args in data["spikes"]]
        # Keep every other coin: fewer pickups make each one feel worthwhile.
        self.coins = [Coin(x, y) for x, y in data["coins"]][::2]
        self.checkpoints = [Checkpoint(x, y) for x, y in data["checkpoints"]]
        self.goal = Goal(*data["goal"])
        self.total_coins = len(self.coins)
        self.coins_collected = 0
        self.time = 0.0
        self.clock = 0.0

        rng = random.Random(data.get("seed", 1))
        self.clouds = []
        for _ in range(16):
            self.clouds.append((
                rng.uniform(-100, self.width * 0.8 + WIDTH),
                rng.uniform(42, 300),
                rng.uniform(0.55, 1.35),
                rng.uniform(0.07, 0.2),
                rng.uniform(0, math.tau),
            ))
        self.hill_phase = rng.uniform(0, math.tau)
        self.hill_phase2 = rng.uniform(0, math.tau)
        self.bush_seed = rng.randrange(1, 10_000)

    def update(self):
        for platform in self.moving:
            platform.update()
        self.clock += 1.0 / 60.0
        self.time += 1.0 / 60.0
        for coin in self.coins:
            coin.update(self.clock)

    # --- background ------------------------------------------------------
    def draw_background(self, surface, cam_x, t, with_sun=True, with_clouds=True):
        theme = self.theme
        surface.blit(fx.gradient(WIDTH, HEIGHT, theme["sky_top"], theme["sky_bottom"]), (0, 0))
        if with_sun:
            self._draw_sun(surface, cam_x, t, theme)
        if with_clouds:
            self._draw_clouds(surface, cam_x, t, theme)
        self._draw_hills(surface, cam_x, theme)
        haze = fx.gradient(WIDTH, 160, theme["sky_bottom"], theme["sky_bottom"])
        haze.set_alpha(55)
        surface.blit(haze, (0, 500))

    def _draw_clouds(self, surface, cam_x, t, theme):
        span = self.width * 0.8 + WIDTH + 360
        for x, y, scale, speed, phase in self.clouds:
            sx = (x - cam_x * speed + 180) % span - 180
            if sx < -200 or sx > WIDTH + 200:
                continue
            bob = math.sin(t * 0.55 + phase) * 3
            self._draw_cloud(surface, sx, y + bob, scale, theme)

    def _draw_cloud(self, surface, x, y, scale, theme):
        cream = theme["window"]
        shade = fx.mix(cream, theme["skyline"], 0.13)
        puffs = ((-30, 4, 20), (0, -5, 27), (29, 3, 20), (10, 11, 19))
        for dx, dy, r in puffs:
            pygame.draw.circle(surface, shade,
                               (int(x + dx * scale), int(y + (dy + 5) * scale)),
                               int(r * scale))
        for dx, dy, r in puffs:
            pygame.draw.circle(surface, cream,
                               (int(x + dx * scale), int(y + dy * scale)),
                               int((r - 2) * scale))

    def _draw_hills(self, surface, cam_x, theme):
        self._hill_layer(
            surface, cam_x * 0.10 + self.hill_phase,
            552, 44, 250, theme["skyline"],
            fx.mix(theme["skyline"], theme["window"], 0.25),
        )
        self._hill_layer(
            surface, cam_x * 0.22 + self.hill_phase2,
            590, 56, 170, theme["skyline_light"],
            fx.mix(theme["skyline_light"], theme["platform_light"], 0.32),
        )

    def _hill_layer(self, surface, offset, base_y, amp, period, color, rim):
        points = [(0, HEIGHT), (0, base_y)]
        crest = []
        for sx in range(0, WIDTH + 24, 16):
            wx = sx + offset
            y = (base_y
                 - math.sin(wx / period) * amp
                 - math.sin(wx / (period * 0.43) + 1.3) * amp * 0.35
                 - math.sin(wx / (period * 2.1)) * amp * 0.18)
            crest.append((sx, int(y)))
        points.extend(crest)
        points.append((WIDTH, HEIGHT))
        pygame.draw.polygon(surface, color, points)
        for i in range(len(crest) - 1):
            pygame.draw.line(surface, rim, crest[i], crest[i + 1], 3)

    def _draw_sun(self, surface, cam_x, t, theme):
        radius = 94
        sun = getattr(self, "_sun_surf", None)
        if sun is None:
            size = radius * 2 + 12
            sun = pygame.Surface((size, size), pygame.SRCALPHA)
            c = size // 2
            pygame.draw.circle(sun, theme["sun"], (c, c), radius)
            pygame.draw.circle(sun, fx.mix(theme["sun"], theme["sun_glow"], 0.55), (c, c), int(radius * 0.78))
            pygame.draw.circle(sun, fx.mix(theme["sun"], (255, 252, 245), 0.45),
                               (c - radius // 3, c - radius // 3), int(radius * 0.15))
            self._sun_surf = sun
        sx = WIDTH * 0.885 - cam_x * 0.03
        sy = 200
        surface.blit(sun, (int(sx - sun.get_width() // 2), int(sy - sun.get_height() // 2)))

    # --- объекты ---------------------------------------------------------
    def draw(self, surface, offset, t):
        ox, oy = offset
        for platform in self.moving:
            self._draw_rail(surface, platform, ox, oy, t)
        for platform in self.platforms:
            self._draw_platform(surface, platform, ox, oy, t)
        for checkpoint in self.checkpoints:
            checkpoint.draw(surface, offset, self.theme, t)
        for spike in self.spikes:
            spike.draw(surface, offset, self.theme)
        for coin in self.coins:
            if not coin.collected:
                coin.draw(surface, offset, t)
        self.goal.draw(surface, offset, self.theme, t)

    def _draw_rail(self, surface, platform, ox, oy, t):
        rail = fx.mix(self.theme["platform"], (74, 48, 34), 0.45)
        dot = fx.mix(self.theme["edge"], (255, 250, 238), 0.38)
        if platform.dx:
            x1 = platform.base_x - ox
            x2 = platform.base_x + platform.dx + platform.rect.w - ox
            y = platform.base_y + 10 - oy
            pygame.draw.line(surface, rail, (x1, y), (x2, y), 2)
            for i in range(int(x1), int(x2), 28):
                pygame.draw.circle(surface, dot, (i, int(y)), 2)
        elif platform.dy:
            x = platform.base_x + platform.rect.w / 2 - ox
            y1 = platform.base_y + min(0.0, platform.dy) - oy
            y2 = platform.base_y + max(0.0, platform.dy) - oy
            pygame.draw.line(surface, rail, (x, y1), (x, y2), 2)
            for i in range(int(y1), int(y2), 28):
                pygame.draw.circle(surface, dot, (int(x), i), 2)

    def _draw_platform(self, surface, platform, ox, oy, t):
        rect = platform.rect.move(-ox, -oy)
        if rect.right < -40 or rect.left > WIDTH + 40:
            return
        theme = self.theme
        dark = (104, 74, 54)
        light = fx.mix(theme["platform_light"], (255, 250, 238), 0.22)

        if platform.moving:
            body = pygame.Rect(rect.x, rect.y, rect.w, rect.h)
            pygame.draw.rect(surface, (150, 116, 82),
                             (rect.x + 4, rect.bottom + 2, max(4, rect.w - 8), 5), border_radius=3)
            pygame.draw.rect(surface, dark, body.inflate(4, 6), border_radius=9)
            pygame.draw.rect(surface, theme["platform_light"], body, border_radius=8)
            pygame.draw.rect(surface, fx.mix(theme["accent"], dark, 0.35),
                             body, width=2, border_radius=8)
            pygame.draw.rect(surface, light, (rect.x + 6, rect.y + 3, rect.w - 12, 3),
                             border_radius=2)
            for i in range(rect.x + 12, rect.right - 8, 20):
                pygame.draw.line(surface, fx.mix(theme["platform"], dark, 0.25),
                                 (i, rect.y + 8), (i + 6, rect.y + 8), 2)
            for i in (10, rect.w - 10):
                pygame.draw.circle(surface, theme["accent"], (rect.x + i, rect.y + 7), 2)
            return

        if platform.one_way:
            body = pygame.Rect(rect.x, rect.y, rect.w, max(platform.rect.h, 16))
            pygame.draw.rect(surface, dark, body.inflate(0, 5), border_radius=8)
            pygame.draw.rect(surface, theme["platform"], body, border_radius=7)
            pygame.draw.rect(surface, theme["edge"],
                             (rect.x + 2, rect.y + 1, rect.w - 4, 6), border_radius=4)
            pygame.draw.line(surface, light, (rect.x + 8, rect.y + 2),
                             (rect.right - 8, rect.y + 2), 1)
            for gx in range(rect.x + 12, rect.right - 8, 34):
                blade = 4 + (gx * 13) % 5
                pygame.draw.line(surface, theme["edge"], (gx, rect.y + 1),
                                 (gx - 2, rect.y - blade), 2)
                if (gx // 34) % 3 == 0:
                    pygame.draw.circle(surface, theme["accent"], (gx + 7, rect.y - 2), 2)
            for gy in range(rect.y + 12, rect.bottom - 3, 9):
                pygame.draw.line(surface, fx.mix(theme["platform"], theme["platform_light"], 0.35),
                                 (rect.x + 6, gy), (rect.right - 6, gy), 1)
            pygame.draw.line(surface, fx.mix(theme["platform"], dark, 0.35),
                             (rect.x + 8, rect.bottom - 2), (rect.right - 8, rect.bottom - 2), 1)
            return

        # ground
        pygame.draw.rect(surface, theme["platform"], rect)
        for gy in range(rect.y + 20, rect.bottom, 26):
            pygame.draw.line(surface, fx.mix(theme["platform"], theme["platform_light"], 0.38),
                             (rect.x, gy), (rect.right, gy), 1)
        for gx in range(rect.x + 30, rect.right, 72):
            py = rect.y + 24 + (gx * 19) % max(8, rect.h - 32)
            pygame.draw.circle(surface, fx.mix(theme["platform"], dark, 0.3), (gx, py), 2)
        pygame.draw.rect(surface, fx.mix(theme["platform"], dark, 0.22),
                         (rect.x, rect.bottom - 18, rect.w, 18))
        pygame.draw.rect(surface, theme["edge"],
                         (rect.x, rect.y, rect.w, 9))
        pygame.draw.line(surface, light, (rect.x + 2, rect.y + 2),
                         (rect.right - 2, rect.y + 2), 1)
        for gx in range(rect.x + 16, rect.right, 28):
            blade = 5 + (gx * 7) % 6
            pygame.draw.line(surface, theme["edge"], (gx, rect.y + 2),
                             (gx - 2, rect.y - blade), 2)
        for gx in range(rect.x + 52, rect.right, 132):
            pygame.draw.circle(surface, theme["accent"], (gx, rect.y - 4), 3)
            pygame.draw.circle(surface, (255, 238, 196), (gx, rect.y - 4), 1)

    def draw_foreground(self, surface, offset, t):
        # warm, gentle bottom vignette (no neon/black)
        shade = pygame.Surface((WIDTH, 64), pygame.SRCALPHA)
        for i in range(64):
            alpha = int(26 * (i / 64) ** 2)
            pygame.draw.line(shade, (92, 64, 44, alpha), (0, i), (WIDTH, i))
        surface.blit(shade, (0, HEIGHT - 64))
