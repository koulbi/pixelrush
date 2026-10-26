"""Visual effects: particles, camera, gradients, panels and shadows."""
import math
import random

import pygame

from config import FONT_BOLD, HEIGHT, WIDTH

# --- маленькие утилиты ---------------------------------------------------
def clamp(value, low, high):
    return low if value < low else high if value > high else value


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def ease_out(t):
    t = clamp(t, 0.0, 1.0)
    return 1 - (1 - t) ** 3


def hsva(hue, sat=100, val=100, alpha=100):
    color = pygame.Color(0, 0, 0)
    color.hsva = (hue % 360, sat, val, alpha)
    return color


# --- кэши ----------------------------------------------------------------
_grad_cache = {}
_dot_cache = {}
_star_cache = {}
_ellipse_cache = {}
_text_cache = {}
_font_cache = {}
_scan_cache = {}


def gradient(width, height, top, bottom):
    key = (width, height, top, bottom)
    surf = _grad_cache.get(key)
    if surf is None:
        surf = pygame.Surface((width, height))
        for y in range(height):
            color = mix(top, bottom, y / max(1, height - 1))
            pygame.draw.line(surf, color, (0, y), (width, y))
        _grad_cache[key] = surf
    return surf


def glow_dot(color, radius):
    """A flat, friendly dot used for particles (kept name for compatibility)."""
    radius = max(2, int(radius))
    key = (tuple(color), radius)
    surf = _dot_cache.get(key)
    if surf is None:
        size = radius * 2 + 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        pygame.draw.circle(surf, (*color, 255), (center, center), radius)
        if radius >= 4:
            pygame.draw.circle(
                surf, (*mix(color, (255, 252, 245), 0.35), 210),
                (center - radius // 3, center - radius // 3),
                max(1, radius // 3),
            )
        _dot_cache[key] = surf
    return surf


def star_surface(color, radius):
    radius = max(3, int(radius))
    key = (tuple(color), radius)
    surf = _star_cache.get(key)
    if surf is None:
        size = radius * 2 + 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        points = []
        for i in range(8):
            ang = -math.pi / 2 + i * math.pi / 4
            r = radius if i % 2 == 0 else radius * 0.38
            points.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        pygame.draw.polygon(surf, (*color, 255), points)
        _star_cache[key] = surf
    return surf


def soft_ellipse(width, height, color=(0, 0, 0), alpha=90):
    key = (width, height, tuple(color), alpha)
    surf = _ellipse_cache.get(key)
    if surf is None:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (*color, alpha), surf.get_rect())
        _ellipse_cache[key] = surf
    return surf


def scanlines(width, height, step=4, alpha=14):
    # Kept for API compatibility; the new art direction has no scanlines.
    return pygame.Surface((width, height), pygame.SRCALPHA)


def _font(size):
    font = _font_cache.get(size)
    if font is None:
        font = pygame.font.Font(FONT_BOLD, size)
        _font_cache[size] = font
    return font


# --- панели --------------------------------------------------------------
_panel_cache = {}


def panel_surface(width, height, top, bottom, radius=18):
    key = (width, height, tuple(top), tuple(bottom), radius)
    surf = _panel_cache.get(key)
    if surf is not None:
        return surf
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        color = mix(top, bottom, y / max(1, height - 1))
        pygame.draw.line(surf, (*color, 244), (0, y), (width, y))
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if len(_panel_cache) > 60:
        _panel_cache.clear()
    _panel_cache[key] = surf
    return surf


def draw_glow_border(surface, rect, color, radius=18, strength=1.0):
    """Soft, warm drop shadow (no neon glow)."""
    pad = 24
    tmp = pygame.Surface((rect.w + pad * 2, rect.h + pad * 2), pygame.SRCALPHA)
    for i in range(10, 0, -1):
        alpha = int(4 * strength)
        r = pygame.Rect(
            pad - i + 2, pad + 5 + i // 2,
            rect.w + i * 2, rect.h + i * 2,
        )
        pygame.draw.rect(tmp, (74, 52, 38, alpha), r, border_radius=radius + i)
    surface.blit(tmp, (rect.x - pad, rect.y - pad))


def draw_panel(surface, rect, border=(72, 145, 146), t=0.0, radius=18, glow=True):
    if glow:
        draw_glow_border(surface, rect, border, radius, 1.0)
    panel = panel_surface(rect.w, rect.h, (255, 253, 247), (253, 240, 224), radius)
    surface.blit(panel, rect.topleft)
    pygame.draw.rect(surface, (*border, 255), rect, width=2, border_radius=radius)
    # gentle top highlight
    line = pygame.Surface((max(1, rect.w - 28), 1), pygame.SRCALPHA)
    line.fill((255, 255, 255, 150))
    surface.blit(line, (rect.x + 14, rect.y + 2))


# --- частицы -------------------------------------------------------------
class Particle:
    __slots__ = (
        "x", "y", "vx", "vy", "life", "max_life", "color", "size",
        "gravity", "drag", "kind", "text", "font_size",
    )

    def __init__(self, x, y, vx, vy, life, color, size,
                 gravity=0.0, drag=1.0, kind="dot", text=None, font_size=18):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.drag = drag
        self.kind = kind
        self.text = text
        self.font_size = font_size


class Particles:
    def __init__(self):
        self.items = []

    def clear(self):
        self.items.clear()

    def add(self, particle):
        if len(self.items) < 700:
            self.items.append(particle)

    def burst(self, x, y, color, count=14, speed=(1.5, 5.0), life=(18, 38),
              size=(2.0, 5.0), gravity=0.16, angle=None, spread=math.tau):
        for _ in range(count):
            if angle is None:
                a = random.uniform(0, math.tau)
            else:
                a = angle + random.uniform(-spread / 2, spread / 2)
            sp = random.uniform(*speed)
            self.add(Particle(
                x, y, math.cos(a) * sp, math.sin(a) * sp,
                random.randint(*life), color, random.uniform(*size),
                gravity=gravity,
            ))

    def stars(self, x, y, color, count=8, speed=(1.0, 4.0), life=(20, 45), size=(3, 6)):
        for _ in range(count):
            a = random.uniform(0, math.tau)
            sp = random.uniform(*speed)
            self.add(Particle(
                x, y, math.cos(a) * sp, math.sin(a) * sp,
                random.randint(*life), color, random.randint(*size),
                gravity=0.05, kind="star",
            ))

    def dust(self, x, y, color, direction=0, count=6):
        for _ in range(count):
            a = -math.pi / 2 + direction * 0.7 + random.uniform(-0.5, 0.5)
            sp = random.uniform(0.8, 2.6)
            self.add(Particle(
                x + random.uniform(-8, 8), y,
                math.cos(a) * sp, math.sin(a) * sp,
                random.randint(14, 26), color, random.uniform(2, 4),
                gravity=0.02,
            ))

    def confetti(self, count=40):
        colors = [(238, 111, 94), (245, 194, 78), (100, 156, 92),
                  (114, 180, 220), (178, 151, 214), (250, 170, 140)]
        for _ in range(count):
            self.add(Particle(
                random.uniform(0, WIDTH), random.uniform(-60, 80),
                random.uniform(-1.4, 1.4), random.uniform(1.5, 4.5),
                random.randint(70, 140), random.choice(colors),
                random.uniform(2, 5), gravity=0.03, drag=0.995,
            ))

    def text_pop(self, x, y, text, color, size=20, life=50):
        self.add(Particle(
            x, y, random.uniform(-0.3, 0.3), -1.3, life, color, 0,
            gravity=0.0, drag=0.99, kind="text", text=text, font_size=size,
        ))

    def update(self):
        alive = []
        for p in self.items:
            p.x += p.vx
            p.y += p.vy
            p.vy += p.gravity
            p.vx *= p.drag
            p.vy *= p.drag
            p.life -= 1
            if p.life > 0:
                alive.append(p)
        self.items = alive

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        for p in self.items:
            t = p.life / p.max_life
            alpha = int(255 * (t ** 0.7))
            x = int(p.x - ox)
            y = int(p.y - oy)
            if p.kind == "text":
                img = _text_cache.get((p.text, p.font_size, p.color))
                if img is None:
                    img = _font(p.font_size).render(p.text, True, p.color)
                    _text_cache[(p.text, p.font_size, p.color)] = img
                img.set_alpha(alpha)
                surface.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
            elif p.kind == "star":
                img = star_surface(p.color, int(p.size))
                img.set_alpha(alpha)
                surface.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
            else:
                img = glow_dot(p.color, int(p.size))
                img.set_alpha(alpha)
                surface.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))


# --- камера --------------------------------------------------------------
class Camera:
    def __init__(self, x=0.0):
        self.x = float(x)
        self.shake = 0.0

    def snap(self, target_x, level_width):
        self.x = clamp(target_x - WIDTH * 0.42, 0, max(0, level_width - WIDTH))

    def update(self, target_x, level_width, look_ahead=0.0):
        target = clamp(target_x + look_ahead - WIDTH * 0.42, 0, max(0, level_width - WIDTH))
        self.x += (target - self.x) * 0.12
        self.shake *= 0.87
        if self.shake < 0.15:
            self.shake = 0.0

    def add_shake(self, amount):
        self.shake = min(24.0, self.shake + amount)

    def offset(self):
        if self.shake <= 0.2:
            return (0, 0)
        s = self.shake
        return (int(random.uniform(-s, s)), int(random.uniform(-s, s)))
