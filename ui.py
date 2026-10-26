"""Interface: menu, wardrobe, HUD, pause, finish and the cheat menu."""
import math

import pygame

import fx
import player as player_mod
from config import (
    CATEGORIES, CHEAT_ACCENT, CREAM, EYES, FONT_BOLD, FONT_REGULAR, HATS,
    INK, MUTED, NEON_CYAN, NEON_GOLD, NEON_GREEN, NEON_PINK, NEON_RED,
    PALETTES, PANEL, PANEL_LIGHT, SOFT, WHITE, WIDTH, HEIGHT,
)

_fonts = {}
_text_cache = {}
CHEAT_RECT = pygame.Rect(WIDTH // 2 - 280, 105, 560, 512)
SETTINGS_RECT = pygame.Rect(340, 150, 600, 440)
HINT = (255, 244, 226)
DARK_LINE = (196, 176, 154)
GOLD_INK = (170, 108, 34)


def font(size, bold=False):
    key = (size, bold)
    entry = _fonts.get(key)
    if entry is None:
        entry = pygame.font.Font(FONT_BOLD if bold else FONT_REGULAR, size)
        _fonts[key] = entry
    return entry


def render(txt, size, color, bold=False):
    key = (txt, size, tuple(color), bold)
    img = _text_cache.get(key)
    if img is None:
        img = font(size, bold).render(txt, True, color)
        if len(_text_cache) > 900:
            _text_cache.clear()
        _text_cache[key] = img
    return img


def text(surface, txt, size, color, pos, anchor="topleft", bold=False, alpha=255):
    img = render(txt, size, color, bold)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surface.blit(img, rect)
    return rect


def _card(surface, rect, border, radius=12, selected=False, shadow=True):
    if shadow:
        fx.draw_glow_border(surface, rect, border, radius=radius, strength=0.7)
    surface.blit(fx.panel_surface(rect.w, rect.h, (255, 252, 246), (250, 238, 222), radius),
                 rect.topleft)
    pygame.draw.rect(surface, border, rect, 2 if selected else 1, border_radius=radius)


def draw_coin(surface, center, radius=12, t=0.0):
    x, y = int(center[0]), int(center[1])
    spin = max(0.28, abs(math.cos(t * 2.2)))
    rx = max(2, int(radius * spin))
    pygame.draw.ellipse(surface, (132, 82, 38),
                        (x - rx - 2, y - radius - 2, rx * 2 + 4, radius * 2 + 4))
    pygame.draw.ellipse(surface, (238, 174, 58),
                        (x - rx, y - radius, rx * 2, radius * 2))
    if rx > radius * 0.5:
        pygame.draw.ellipse(surface, (255, 220, 120),
                            (x - rx + 2, y - radius + 3, max(1, rx - 2), radius * 2 - 6))
        pygame.draw.ellipse(surface, (255, 250, 220),
                            (x - rx + 2, y - radius + 5, max(1, rx // 2), radius - 2))
    pygame.draw.ellipse(surface, (255, 240, 170),
                        (x - rx, y - radius, rx * 2, radius * 2), 1)


def draw_lock(surface, center, color=(255, 250, 238), size=10):
    x, y = int(center[0]), int(center[1])
    pygame.draw.rect(surface, color, (x - size // 2, y - 1, size, size - 1), border_radius=2)
    pygame.draw.arc(surface, color, (x - size // 2 + 1, y - size, size - 2, size),
                    0.05, math.pi - 0.05, 2)
    pygame.draw.circle(surface, (74, 52, 38), (x, y + 2), 1)


def draw_button(surface, rect, label, selected, accent=NEON_CYAN, size=22, t=0.0):
    hover = rect.collidepoint(pygame.mouse.get_pos())
    active = selected or hover
    if active:
        fx.draw_glow_border(surface, rect, accent, radius=14, strength=0.9)
        pygame.draw.rect(surface, accent, rect, border_radius=14)
        pygame.draw.line(surface, fx.mix(accent, (255, 252, 245), 0.32),
                         (rect.x + 14, rect.y + 3), (rect.right - 14, rect.y + 3), 2)
        pygame.draw.rect(surface, fx.mix(accent, INK, 0.28), rect, 2, border_radius=14)
        text(surface, label, size, CREAM, rect.center, "center", bold=True)
    else:
        surface.blit(fx.panel_surface(rect.w, rect.h, (255, 251, 243), (247, 234, 218), 14),
                     rect.topleft)
        pygame.draw.rect(surface, DARK_LINE, rect, 1, border_radius=14)
        text(surface, label, size, INK, rect.center, "center", bold=True)
    if selected:
        wobble = int(math.sin(t * 6) * 2)
        pygame.draw.polygon(surface, accent, [
            (rect.x - 22 + wobble, rect.centery - 7),
            (rect.x - 22 + wobble, rect.centery + 7),
            (rect.x - 7 + wobble, rect.centery),
        ])


def _backdrop(surface, game, dim=68, with_sun=True, with_clouds=True):
    level = game.backdrop
    cam = (game.ui_t * 18) % max(1, level.width - WIDTH)
    level.draw_background(surface, cam, game.ui_t, with_sun=with_sun, with_clouds=with_clouds)
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((54, 40, 32, dim))
    surface.blit(shade, (0, 0))


def _coin_pill(surface, game, right=34, top=28, width=150):
    rect = pygame.Rect(WIDTH - right - width, top, width, 48)
    surface.blit(fx.panel_surface(rect.w, rect.h, (255, 252, 246), (250, 238, 222), 16),
                 rect.topleft)
    pygame.draw.rect(surface, DARK_LINE, rect, 1, border_radius=16)
    draw_coin(surface, (rect.x + 27, rect.centery), 12, game.ui_t)
    text(surface, f"{game.save.coins}", 21, INK, (rect.x + 49, rect.centery - 5),
         "midleft", bold=True)
    text(surface, "COINS", 10, MUTED, (rect.x + 50, rect.centery + 13), "midleft")
    return rect


def _keycap(surface, center, label, size=34, color=NEON_CYAN):
    rect = pygame.Rect(0, 0, size, size)
    rect.center = center
    pygame.draw.rect(surface, (255, 250, 240), rect, border_radius=8)
    pygame.draw.rect(surface, color, rect, 2, border_radius=8)
    text(surface, label, max(12, size // 2), INK, rect.center, "center", bold=True)


# ---------------------------------------------------------------------------
#  Menu
# ---------------------------------------------------------------------------
def draw_menu(game, surface):
    t = game.ui_t
    _backdrop(surface, game, 62)
    theme = game.backdrop.theme

    # ground band
    pygame.draw.rect(surface, theme["platform"], (0, 646, WIDTH, 74))
    pygame.draw.rect(surface, fx.mix(theme["platform"], (78, 50, 34), 0.28),
                     (0, 700, WIDTH, 20))
    pygame.draw.rect(surface, theme["edge"], (0, 642, WIDTH, 8))
    pygame.draw.line(surface, fx.mix(theme["edge"], CREAM, 0.55),
                     (0, 644), (WIDTH, 644), 2)
    for gx in range(24, WIDTH, 54):
        blade = 5 + (gx * 7) % 6
        pygame.draw.line(surface, theme["edge"], (gx, 644), (gx - 2, 644 - blade), 2)
    for gx in range(52, WIDTH, 146):
        pygame.draw.circle(surface, theme["accent"], (gx, 639), 3)
        pygame.draw.circle(surface, (255, 238, 196), (gx, 639), 1)

    # little stage for the hero
    plat = pygame.Rect(908, 600, 290, 18)
    pygame.draw.rect(surface, (112, 76, 52), plat.inflate(0, 6), border_radius=8)
    pygame.draw.rect(surface, theme["platform"], plat, border_radius=7)
    pygame.draw.rect(surface, theme["edge"], (plat.x + 2, plat.y + 1, plat.w - 4, 6),
                     border_radius=4)
    for gx in range(plat.x + 14, plat.right - 8, 34):
        blade = 4 + (gx * 11) % 5
        pygame.draw.line(surface, theme["edge"], (gx, plat.y + 1),
                         (gx - 2, plat.y - blade), 2)
        if (gx // 34) % 3 == 0:
            pygame.draw.circle(surface, theme["accent"], (gx + 7, plat.y - 2), 2)

    bounce = math.sin(t * 2.4) * 5
    preview_center = (1053, 600 - 56 + bounce)
    player_mod.draw_character(
        surface, preview_center, (92, 112), PALETTES[game.save.equipped("skin")],
        hat=game.save.equipped("hat"), eyes=game.save.equipped("eyes"),
        facing=1, t=t, squash=1.0, walk=math.sin(t * 3) * 0.4,
    )
    for cx, cy, phase in ((915, 500, 0.0), (1210, 470, 1.7), (975, 420, 3.2)):
        cy += math.sin(t * 2 + phase) * 7
        draw_coin(surface, (cx, cy), 11, t + phase)

    # title
    title = "PIXELRUSH"
    text(surface, title, 104, (86, 58, 42), (WIDTH // 2 + 5, 163), "center",
         bold=True, alpha=135)
    text(surface, title, 104, CREAM, (WIDTH // 2, 156), "center", bold=True)
    text(surface, "a colorful little platformer  ·  spikes, coins & cheats", 21, (86, 58, 42),
         (WIDTH // 2 + 2, 240), "center", alpha=140)
    text(surface, "a colorful little platformer  ·  spikes, coins & cheats", 21, HINT,
         (WIDTH // 2, 238), "center", alpha=235)
    line_w = 300
    pygame.draw.line(surface, theme["accent"], (WIDTH // 2 - line_w, 266),
                     (WIDTH // 2 - 30, 266), 2)
    pygame.draw.line(surface, theme["edge"], (WIDTH // 2 + 30, 266),
                     (WIDTH // 2 + line_w, 266), 2)
    pygame.draw.circle(surface, CREAM, (WIDTH // 2, 266), 3)

    labels = ("PLAY", "WARDROBE", "SETTINGS", "QUIT")
    colors = (theme["edge"], theme["accent"], NEON_GOLD, (130, 118, 108))
    for i, label in enumerate(labels):
        rect = pygame.Rect(WIDTH // 2 - 170, 300 + i * 68, 340, 56)
        game.hotspots.append((rect, "menu", i))
        draw_button(surface, rect, label, game.menu_index == i, colors[i], 22, t)
    text(surface, "↑ ↓ to choose   ·   ENTER to confirm", 14, (86, 58, 42),
         (WIDTH // 2 + 1, 589), "center", alpha=150)
    text(surface, "↑ ↓ to choose   ·   ENTER to confirm", 14, HINT,
         (WIDTH // 2, 588), "center", alpha=215)

    _coin_pill(surface, game)

    # cheat menu hint
    hint_rect = pygame.Rect(34, 620, 300, 52)
    surface.blit(fx.panel_surface(hint_rect.w, hint_rect.h, (255, 251, 243), (247, 234, 218), 14),
                 hint_rect.topleft)
    pygame.draw.rect(surface, DARK_LINE, hint_rect, 1, border_radius=14)
    game.hotspots.append((hint_rect, "cheat_open", None))
    _keycap(surface, (hint_rect.x + 30, hint_rect.centery), "\\", 32, CHEAT_ACCENT)
    text(surface, "CHEAT MENU", 17, INK, (hint_rect.x + 56, hint_rect.centery - 8),
         "midleft", bold=True)
    text(surface, "small but handy", 12, MUTED, (hint_rect.x + 56, hint_rect.centery + 10),
         "midleft")
    text(surface, "M — sound", 12, HINT, (WIDTH - 34, HEIGHT - 24), "bottomright", alpha=210)


# ---------------------------------------------------------------------------
#  Settings
# ---------------------------------------------------------------------------
def draw_settings(game, surface):
    t = game.ui_t
    _backdrop(surface, game, 58, with_clouds=False)
    accent = game.backdrop.theme["edge"]

    text(surface, "SETTINGS", 52, (86, 58, 42), (WIDTH // 2 + 3, 76), "center",
         bold=True, alpha=130)
    text(surface, "SETTINGS", 52, CREAM, (WIDTH // 2, 74), "center", bold=True)
    text(surface, "display, sound and a little comfort", 16, (86, 58, 42),
         (WIDTH // 2 + 1, 124), "center", alpha=140)
    text(surface, "display, sound and a little comfort", 16, HINT,
         (WIDTH // 2, 122), "center", alpha=230)

    panel = SETTINGS_RECT
    pygame.draw.rect(surface, (255, 249, 239), panel, border_radius=24)
    fx.draw_panel(surface, panel, accent, t, radius=24)
    rows_top = panel.y + 22
    for i, item in enumerate(game.settings_items):
        row = pygame.Rect(panel.x + 24, rows_top + i * 54, panel.w - 48, 44)
        game.hotspots.append((row, "setting", i))
        selected = i == game.settings_index
        hover = row.collidepoint(pygame.mouse.get_pos())
        if selected or hover:
            surface.blit(fx.panel_surface(row.w, row.h, (255, 251, 243),
                                          (248, 234, 216), 10), row.topleft)
            if selected:
                pygame.draw.rect(surface, accent, (row.x, row.y, 4, row.h),
                                 border_radius=2)
            pygame.draw.rect(surface, fx.mix(accent, CREAM, 0.55), row, 1,
                             border_radius=10)
        text(surface, item["name"], 18, INK, (row.x + 16, row.centery),
             "midleft", bold=selected)
        value = game.settings_value(i)
        state_label = "ON" if value else "OFF"
        text(surface, state_label, 12, NEON_GREEN if value else MUTED,
             (row.right - 82, row.centery), "midright", bold=True)
        switch = pygame.Rect(row.right - 64, row.centery - 9, 46, 18)
        draw_switch(surface, switch, 1.0 if value else 0.0, accent)

    desc = game.settings_items[game.settings_index]["desc"]
    text(surface, desc, 13, SOFT, (panel.x + 26, panel.y + 296), "topleft")

    back = pygame.Rect(panel.centerx - 110, panel.y + 334, 220, 50)
    game.hotspots.append((back, "settings_back", None))
    draw_button(surface, back, "BACK", False, NEON_CYAN, 19, t)
    text(surface, "changes are saved automatically", 11, MUTED,
         (panel.centerx, panel.bottom - 20), "midbottom")

    text(surface, "↑↓ choose   ·   ENTER toggle   ·   ESC back", 12,
         (86, 58, 42), (WIDTH // 2 + 1, HEIGHT - 17), "midbottom", alpha=150)
    text(surface, "↑↓ choose   ·   ENTER toggle   ·   ESC back", 12, HINT,
         (WIDTH // 2, HEIGHT - 18), "midbottom", alpha=215)


# ---------------------------------------------------------------------------
#  Wardrobe
# ---------------------------------------------------------------------------
def _head_preview(surface, center, palette, hat, eyes, t, radius=16):
    cx, cy = center
    dark = fx.mix(palette["body"], (52, 38, 30), 0.55)
    pygame.draw.circle(surface, dark, (cx, cy), radius + 3)
    pygame.draw.circle(surface, palette["body"], (cx, cy), radius)
    hi = pygame.Rect(cx - int(radius * 0.55), cy - int(radius * 0.66),
                     max(3, int(radius * 0.55)), max(2, int(radius * 0.3)))
    pygame.draw.ellipse(surface, fx.mix(palette["body"], (255, 252, 245), 0.45), hi)
    w, h = radius * 2.0, radius * 2.15
    player_mod._draw_eyes(surface, cx, cy, w, h, eyes, 1, t, False)
    player_mod._draw_hat(surface, cx, cy, w, h, hat, palette["accent"], palette["body"], t)


def draw_customize(game, surface):
    t = game.ui_t
    _backdrop(surface, game, 88, with_sun=False)
    accent = PALETTES[game.custom_sel[0]]["accent"]
    theme_accent = game.backdrop.theme["edge"]

    text(surface, "WARDROBE", 52, (86, 58, 42), (67, 51), "topleft", bold=True, alpha=130)
    text(surface, "WARDROBE", 52, CREAM, (64, 46), "topleft", bold=True)
    text(surface, "build your colorful hero", 16, (86, 58, 42), (67, 106), "topleft",
         alpha=130)
    text(surface, "build your colorful hero", 16, HINT, (66, 104), "topleft", alpha=230)
    _coin_pill(surface, game)

    # left showcase
    preview_rect = pygame.Rect(64, 142, 468, 486)
    fx.draw_glow_border(surface, preview_rect, accent, radius=22, strength=1.0)
    surface.blit(fx.panel_surface(preview_rect.w, preview_rect.h, (255, 252, 246),
                                  (248, 234, 216), 22), preview_rect.topleft)
    pygame.draw.rect(surface, accent, preview_rect, 2, border_radius=22)
    halo_color = fx.mix(PANEL, accent, 0.18)
    pygame.draw.circle(surface, halo_color, (preview_rect.centerx, 344), 154)
    pygame.draw.circle(surface, fx.mix(halo_color, CREAM, 0.35),
                       (preview_rect.centerx, 344), 132)
    if game.save.setting("particles"):
        for i in range(14):
            ang = t * 0.6 + i * math.tau / 14
            rr = 172 + math.sin(t * 1.2 + i) * 10
            px = preview_rect.centerx + math.cos(ang) * rr
            py = 344 + math.sin(ang) * rr * 0.72
            color = accent if i % 3 == 0 else fx.mix(theme_accent, CREAM, 0.4)
            pygame.draw.circle(surface, color, (int(px), int(py)), 2)

    # podium
    ped = pygame.Rect(preview_rect.centerx - 130, 520, 260, 26)
    pygame.draw.ellipse(surface, (150, 116, 82), (ped.x, ped.y + 8, ped.w, 26))
    pygame.draw.ellipse(surface, fx.mix(accent, CREAM, 0.35), ped)
    pygame.draw.ellipse(surface, accent, ped, 2)
    text(surface, "PREVIEW", 11, MUTED, (preview_rect.centerx, 566), "center")

    player_mod.draw_character(
        surface, (preview_rect.centerx, 447), (126, 150),
        PALETTES[game.custom_sel[0]], hat=game.custom_sel[1], eyes=game.custom_sel[2],
        facing=1, t=t, walk=math.sin(t * 2.2) * 0.3,
    )

    # cards
    x0 = 576
    available = WIDTH - 34 - x0
    for ci, cat in enumerate(CATEGORIES):
        label_y = 148 + ci * 132
        sel_index = game.custom_sel[ci]
        category_color = accent if ci == 0 else theme_accent
        text(surface, cat["label"], 14, INK, (x0, label_y), "topleft", bold=True)
        count = len(cat["items"])
        equipped = game.save.equipped(cat["equip"])
        text(surface, f"{sum(1 for i in range(count) if game.save.is_unlocked(cat['key'], i))}/{count}",
             12, INK, (x0 + available, label_y + 2), "topright")
        card_w = 62
        spacing = min(80, (available - card_w) // max(1, count - 1))
        for idx, item in enumerate(cat["items"]):
            card = pygame.Rect(x0 + idx * spacing, label_y + 28, card_w, 64)
            game.hotspots.append((card, "custom_item", (ci, idx)))
            selected = idx == sel_index
            hover = card.collidepoint(pygame.mouse.get_pos())
            unlocked = game.save.is_unlocked(cat["key"], idx)
            border = category_color if selected else (DARK_LINE if hover else (216, 198, 178))
            _card(surface, card, border, radius=12, selected=selected,
                  shadow=selected)
            if ci == 0:
                palette = item
                pygame.draw.circle(surface, fx.mix(palette["body"], (52, 38, 30), 0.55),
                                   (card.centerx, card.centery - 3), 19)
                pygame.draw.circle(surface, palette["body"],
                                   (card.centerx, card.centery - 3), 16)
                pygame.draw.circle(surface, fx.mix(palette["body"], (255, 252, 245), 0.45),
                                   (card.centerx - 5, card.centery - 9), 4)
            else:
                palette = PALETTES[game.custom_sel[0]]
                _head_preview(surface, (card.centerx, card.centery - 4), palette,
                              idx if ci == 1 else game.custom_sel[1],
                              idx if ci == 2 else game.custom_sel[2], t, 15)
            if not unlocked:
                shade = pygame.Surface((card.w, card.h), pygame.SRCALPHA)
                pygame.draw.rect(shade, (62, 44, 32, 118), (0, 0, card.w, card.h),
                                 border_radius=12)
                surface.blit(shade, card.topleft)
                draw_lock(surface, (card.right - 12, card.y + 12), (255, 250, 238), 9)
                price_color = GOLD_INK if game.save.coins >= item["price"] else NEON_RED
                text(surface, str(item["price"]), 11, price_color,
                     (card.centerx, card.bottom - 9), "center", bold=True)
            if selected:
                pygame.draw.rect(surface, category_color,
                                 (card.x + 12, card.bottom - 4, card.w - 24, 3),
                                 border_radius=2)
                if equipped == idx:
                    pygame.draw.circle(surface, category_color,
                                       (card.right - 8, card.y + 8), 4)

    # selected item status
    cat = CATEGORIES[game.custom_cat]
    item = cat["items"][game.custom_sel[game.custom_cat]]
    status_rect = pygame.Rect(x0, 536, available, 62)
    _card(surface, status_rect, DARK_LINE, radius=14, shadow=False)
    text(surface, item["name"], 19, INK, (status_rect.x + 18, status_rect.centery - 2),
         "midleft", bold=True)
    unlocked = game.save.is_unlocked(cat["key"], game.custom_sel[game.custom_cat])
    equipped = game.save.equipped(cat["equip"]) == game.custom_sel[game.custom_cat]
    if unlocked:
        label = "EQUIPPED" if equipped else "OWNED · ENTER TO WEAR"
        color = NEON_GREEN if equipped else SOFT
        text(surface, label, 14, color, (status_rect.right - 18, status_rect.centery),
             "midright", bold=True)
    else:
        price = item["price"]
        draw_coin(surface, (status_rect.right - 142, status_rect.centery), 9, t)
        text(surface, str(price), 16, GOLD_INK if game.save.coins >= price else NEON_RED,
             (status_rect.right - 128, status_rect.centery), "midleft", bold=True)
        if game.save.coins >= price:
            text(surface, "ENTER TO BUY", 13, NEON_GREEN,
                 (status_rect.right - 18, status_rect.centery), "midright", bold=True)
        else:
            text(surface, "NOT ENOUGH COINS", 13, NEON_PINK,
                 (status_rect.right - 18, status_rect.centery), "midright", bold=True)

    # buttons
    back = pygame.Rect(x0, 616, 200, 52)
    play = pygame.Rect(x0 + available - 200, 616, 200, 52)
    game.hotspots.append((back, "custom_back", None))
    game.hotspots.append((play, "custom_play", None))
    draw_button(surface, back, "BACK", False, (130, 118, 108), 19, t)
    draw_button(surface, play, "PLAY", False, NEON_GREEN, 19, t)
    text(surface, "↑↓ category   ·   ←→ select   ·   ENTER equip/buy   ·   ESC back",
         12, (86, 58, 42), (WIDTH // 2 + 1, HEIGHT - 17), "midbottom", alpha=150)
    text(surface, "↑↓ category   ·   ←→ select   ·   ENTER equip/buy   ·   ESC back",
         12, HINT, (WIDTH // 2, HEIGHT - 18), "midbottom", alpha=215)


# ---------------------------------------------------------------------------
#  HUD
# ---------------------------------------------------------------------------
def fmt_time(seconds):
    minutes = int(seconds // 60)
    rest = seconds - minutes * 60
    return f"{minutes:02d}:{rest:04.1f}"


def draw_hud(game, surface):
    level = game.level
    player = game.player
    theme = level.theme
    edge = theme["edge"]
    t = game.ui_t

    left = pygame.Rect(24, 20, 336, 78)
    surface.blit(fx.panel_surface(left.w, left.h, (255, 252, 246), (250, 238, 222), 16),
                 left.topleft)
    pygame.draw.rect(surface, DARK_LINE, left, 1, border_radius=16)
    pygame.draw.rect(surface, edge, (left.x, left.y + 14, 4, left.h - 28), border_radius=2)
    text(surface, level.name, 17, INK, (left.x + 16, left.y + 14), bold=True)
    text(surface, "TIME", 10, MUTED, (left.x + 16, left.y + 45))
    text(surface, fmt_time(level.time), 18, SOFT, (left.x + 70, left.y + 40), bold=True)
    draw_coin(surface, (left.x + 222, left.y + 53), 10, t)
    text(surface, f"{level.coins_collected}/{level.total_coins}", 16, GOLD_INK,
         (left.x + 238, left.y + 53), "midleft", bold=True)

    right = pygame.Rect(WIDTH - 24 - 240, 20, 240, 78)
    surface.blit(fx.panel_surface(right.w, right.h, (255, 252, 246), (250, 238, 222), 16),
                 right.topleft)
    pygame.draw.rect(surface, DARK_LINE, right, 1, border_radius=16)
    draw_coin(surface, (right.x + 30, right.y + 28), 13, t)
    text(surface, str(game.save.coins), 20, INK, (right.x + 54, right.y + 20), bold=True)
    text(surface, "TOTAL COINS", 9, MUTED, (right.x + 54, right.y + 45))
    text(surface, f"× {game.deaths}", 17, SOFT, (right.right - 18, right.y + 22),
         "topright", bold=True)
    text(surface, "DEATHS", 9, MUTED, (right.right - 18, right.y + 45), "topright")

    # progress
    bar = pygame.Rect(404, 46, 456, 8)
    pygame.draw.rect(surface, (224, 206, 188), bar, border_radius=4)
    ratio = fx.clamp(player.rect.centerx / max(1, level.goal.x), 0.0, 1.0)
    fill_w = int(bar.w * ratio)
    if fill_w > 2:
        fill = fx.gradient(max(2, fill_w), bar.h, theme["accent"], edge)
        surface.blit(fill, (bar.x, bar.y))
        pygame.draw.rect(surface, fx.mix(edge, CREAM, 0.35),
                         (bar.x, bar.y, fill_w, bar.h), 1, border_radius=4)
    pygame.draw.rect(surface, DARK_LINE, bar, 1, border_radius=4)
    marker_x = bar.x + fill_w
    pygame.draw.circle(surface, CREAM, (marker_x, bar.centery), 7)
    pygame.draw.circle(surface, edge, (marker_x, bar.centery), 7, 2)
    pygame.draw.polygon(surface, edge, [
        (bar.right + 8, bar.centery - 8),
        (bar.right + 22, bar.centery - 8),
        (bar.right + 15, bar.centery + 4),
    ])
    text(surface, "LEVEL", 9, MUTED, (bar.x, bar.y - 16))
    text(surface, f"{game.level_index + 1} / 3", 10, SOFT, (bar.right, bar.y - 16),
         "topright")

    active = [item for item in game.cheat_items
              if item["kind"] == "toggle" and game.cheats.get(item["id"])]
    if active:
        text(surface, "CHEATS: " + ", ".join(item["short"] for item in active[:4]), 12,
             CHEAT_ACCENT, (WIDTH // 2, 76), "midtop", bold=True)

    # dash badge (no key hint while playing)
    cx, cy = WIDTH - 58, HEIGHT - 62
    ready = player.dash_cd <= 0
    pygame.draw.circle(surface, (255, 250, 240), (cx, cy), 30)
    pygame.draw.circle(surface, DARK_LINE, (cx, cy), 30, 1)
    if ready:
        pygame.draw.circle(surface, NEON_GOLD, (cx, cy), 27, 2)
    else:
        frac = 1.0 - player.dash_cd / max(1, int(0.8 * 60))
        pygame.draw.arc(surface, NEON_GOLD, (cx - 26, cy - 26, 52, 52),
                        -math.pi / 2, -math.pi / 2 + math.tau * frac, 4)
    bolt = [(cx - 4, cy - 13), (cx + 6, cy - 3), (cx + 1, cy - 2),
            (cx + 6, cy + 12), (cx - 6, cy + 1), (cx - 1, cy + 1)]
    pygame.draw.polygon(surface, NEON_GOLD if ready else (176, 158, 136), bolt)

    if game.save.setting("show_fps"):
        fps_rect = pygame.Rect(24, 104, 82, 22)
        surface.blit(fx.panel_surface(fps_rect.w, fps_rect.h, (255, 251, 243),
                                      (247, 234, 218), 8), fps_rect.topleft)
        pygame.draw.rect(surface, DARK_LINE, fps_rect, 1, border_radius=8)
        text(surface, f"FPS {game.fps:.0f}", 11, INK, fps_rect.center, "center", bold=True)


def draw_level_intro(game, surface):
    frames = game.level_intro
    if frames <= 0:
        return
    total = 130
    elapsed = total - frames
    alpha = 255
    if elapsed < 18:
        alpha = int(255 * elapsed / 18)
    elif frames < 30:
        alpha = int(255 * frames / 30)
    if alpha <= 0:
        return
    rise = int((1 - min(1.0, elapsed / 25)) * 16)
    banner = pygame.Surface((700, 122), pygame.SRCALPHA)
    pygame.draw.rect(banner, (255, 250, 240, int(228 * alpha / 255)),
                     (0, 0, 700, 122), border_radius=24)
    pygame.draw.rect(banner, (*game.level.theme["edge"], int(170 * alpha / 255)),
                     (0, 0, 700, 122), 2, border_radius=24)
    surface.blit(banner, (WIDTH // 2 - 350, 168 - rise))
    text(surface, game.level.name, 46, INK, (WIDTH // 2, 200 - rise), "center",
         bold=True, alpha=alpha)
    text(surface, game.level.subtitle, 17, SOFT, (WIDTH // 2, 248 - rise), "center",
         alpha=alpha)
    pygame.draw.line(surface, game.level.theme["edge"],
                     (WIDTH // 2 - 150, 272 - rise), (WIDTH // 2 + 150, 272 - rise), 1)


# ---------------------------------------------------------------------------
#  Pause
# ---------------------------------------------------------------------------
def draw_pause(game, surface):
    blur = pygame.transform.smoothscale(surface, (WIDTH // 10, HEIGHT // 10))
    blur = pygame.transform.smoothscale(blur, (WIDTH, HEIGHT))
    blur.set_alpha(190)
    surface.blit(blur, (0, 0))
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((42, 30, 24, 115))
    surface.blit(shade, (0, 0))

    panel = pygame.Rect(WIDTH // 2 - 240, 142, 480, 450)
    fx.draw_panel(surface, panel, NEON_CYAN, game.ui_t, radius=22)
    text(surface, "PAUSED", 40, INK, (panel.centerx, panel.y + 44), "center", bold=True)
    text(surface, game.level.name, 14, SOFT, (panel.centerx, panel.y + 84), "center")

    labels = ("RESUME", "RESTART", "WARDROBE", "SETTINGS", "MAIN MENU")
    colors = (NEON_GREEN, NEON_GOLD, NEON_PINK, NEON_CYAN, (130, 118, 108))
    for i, label in enumerate(labels):
        rect = pygame.Rect(panel.x + 60, panel.y + 106 + i * 62, panel.w - 120, 46)
        game.hotspots.append((rect, "pause", i))
        draw_button(surface, rect, label, game.pause_index == i, colors[i], 18, game.ui_t)
    text(surface, "ESC to resume   ·   ↑↓ to choose   ·   ENTER to select",
         12, MUTED, (panel.centerx, panel.bottom - 22), "midbottom")


# ---------------------------------------------------------------------------
#  Cheat menu
# ---------------------------------------------------------------------------
def draw_switch(surface, rect, value, accent):
    value = fx.clamp(value, 0.0, 1.0)
    bg = fx.mix((210, 194, 176), NEON_GREEN, value)
    pygame.draw.rect(surface, bg, rect, border_radius=rect.h // 2)
    pygame.draw.rect(surface, fx.mix(DARK_LINE, accent, value), rect, 1,
                     border_radius=rect.h // 2)
    knob_x = int(fx.lerp(rect.x + rect.h // 2, rect.right - rect.h // 2, value))
    pygame.draw.circle(surface, (120, 92, 70), (knob_x, rect.centery), rect.h // 2 + 1)
    pygame.draw.circle(surface, (255, 250, 240), (knob_x, rect.centery), rect.h // 2 - 2)
    if value > 0.5:
        pygame.draw.circle(surface, NEON_GREEN, (knob_x, rect.centery), 2)


def draw_cheats(game, surface):
    blur = pygame.transform.smoothscale(surface, (WIDTH // 10, HEIGHT // 10))
    blur = pygame.transform.smoothscale(blur, (WIDTH, HEIGHT))
    blur.set_alpha(185)
    surface.blit(blur, (0, 0))
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((42, 30, 24, 105))
    surface.blit(shade, (0, 0))

    panel = CHEAT_RECT
    border = CHEAT_ACCENT
    fx.draw_panel(surface, panel, border, game.ui_t, radius=20)

    # title
    bolt = [(panel.x + 30, panel.y + 22), (panel.x + 42, panel.y + 38),
            (panel.x + 34, panel.y + 38), (panel.x + 44, panel.y + 55),
            (panel.x + 26, panel.y + 35), (panel.x + 34, panel.y + 35)]
    pygame.draw.polygon(surface, NEON_GOLD, bolt)
    text(surface, "CHEAT MENU", 25, INK, (panel.x + 56, panel.y + 20), bold=True)
    text(surface, "\\ / ESC", 12, SOFT, (panel.right - 56, panel.y + 28), "topright")
    close = pygame.Rect(panel.right - 42, panel.y + 8, 30, 30)
    game.hotspots.append((close, "cheat_close", None))
    hover_close = close.collidepoint(pygame.mouse.get_pos())
    pygame.draw.circle(surface, (236, 220, 202) if hover_close else (246, 234, 218),
                       close.center, 13)
    pygame.draw.circle(surface, DARK_LINE, close.center, 13, 1)
    text(surface, "×", 18, INK, close.center, "center", bold=True)
    pygame.draw.line(surface, DARK_LINE, (panel.x + 18, panel.y + 66),
                     (panel.right - 18, panel.y + 66), 1)

    rows_top = panel.y + 76
    for i, item in enumerate(game.cheat_items):
        row = pygame.Rect(panel.x + 16, rows_top + i * 33, panel.w - 32, 30)
        game.hotspots.append((row, "cheat_row", i))
        hover = row.collidepoint(pygame.mouse.get_pos())
        if i == game.cheat_index:
            surface.blit(fx.panel_surface(row.w, row.h, (255, 250, 240),
                                          (249, 235, 217), 8), row.topleft)
            pygame.draw.rect(surface, border, (row.x, row.y, 3, row.h), border_radius=2)
            pygame.draw.rect(surface, fx.mix(border, CREAM, 0.45), row, 1, border_radius=8)
        elif hover:
            surface.blit(fx.panel_surface(row.w, row.h, (255, 252, 246),
                                          (252, 242, 226), 8), row.topleft)

        enabled = item["kind"] == "toggle" and game.cheats.get(item["id"], False)
        dot_color = NEON_GREEN if enabled else (198, 184, 168)
        pygame.draw.rect(surface, dot_color, (row.x + 10, row.centery - 4, 8, 8),
                         border_radius=2)
        text(surface, item["name"], 15, INK if enabled or i == game.cheat_index else SOFT,
             (row.x + 28, row.centery), "midleft", bold=enabled)

        if item["kind"] == "toggle":
            switch = pygame.Rect(row.right - 64, row.centery - 9, 46, 18)
            draw_switch(surface, switch, game.switch_anim[i], border)
        else:
            available = item["id"] != "skip" or game.state == "play"
            pill = pygame.Rect(row.right - 74, row.centery - 11, 56, 22)
            color = border if available else MUTED
            pygame.draw.rect(surface, (255, 250, 240), pill, border_radius=11)
            pygame.draw.rect(surface, color, pill, 1, border_radius=11)
            text(surface, "GO →", 11, color if available else MUTED, pill.center,
                 "center", bold=True)

    desc_y = rows_top + len(game.cheat_items) * 33 + 8
    selected = game.cheat_items[game.cheat_index]
    text(surface, selected["desc"], 13, SOFT, (panel.x + 24, desc_y), "topleft")
    pygame.draw.line(surface, DARK_LINE, (panel.x + 18, desc_y + 28),
                     (panel.right - 18, desc_y + 28), 1)
    hint_y = panel.bottom - 40
    key_names = (("↑↓", "choose"), ("ENTER", "apply"), ("\\", "close"))
    x = panel.x + 24
    for key, label in key_names:
        key_rect = pygame.Rect(x, hint_y + 2, font(11).size(key)[0] + 14, 20)
        pygame.draw.rect(surface, (255, 250, 240), key_rect, border_radius=5)
        pygame.draw.rect(surface, DARK_LINE, key_rect, 1, border_radius=5)
        text(surface, key, 10, SOFT, key_rect.center, "center", bold=True)
        text(surface, label, 11, MUTED, (key_rect.right + 6, key_rect.centery), "midleft")
        x = key_rect.right + 6 + font(11).size(label)[0] + 20
    text(surface, "small but cheaty", 10, (150, 130, 112),
         (panel.right - 22, hint_y + 12), "midright")


# ---------------------------------------------------------------------------
#  Toast notifications
# ---------------------------------------------------------------------------
def draw_toasts(game, surface):
    y = 112
    for toast in game.toasts:
        timer = toast["timer"]
        alpha = 255
        if timer < 24:
            alpha = int(255 * timer / 24)
        if timer > toast["max"] - 12:
            alpha = int(255 * (toast["max"] - timer) / 12)
        alpha = max(0, min(255, alpha))
        label = render(toast["text"], 15, INK, True)
        w = label.get_width() + 58
        rect = pygame.Rect(WIDTH // 2 - w // 2, y, w, 38)
        shadow = pygame.Surface((w + 4, 42), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (74, 52, 38, int(42 * alpha / 255)),
                         (4, 5, w, 38), border_radius=19)
        surface.blit(shadow, rect.topleft)
        pill = pygame.Surface((w, 38), pygame.SRCALPHA)
        pygame.draw.rect(pill, (255, 250, 240, int(245 * alpha / 255)),
                         (0, 0, w, 38), border_radius=19)
        pygame.draw.rect(pill, (*toast["color"], int(210 * alpha / 255)),
                         (0, 0, w, 38), 2, border_radius=19)
        pygame.draw.circle(pill, (*toast["color"], alpha), (20, 19), 5)
        surface.blit(pill, rect.topleft)
        img = label.copy()
        img.set_alpha(alpha)
        surface.blit(img, (rect.x + 34, rect.y + 11))
        y += 46


# ---------------------------------------------------------------------------
#  Level complete / win
# ---------------------------------------------------------------------------
def draw_complete(game, surface):
    blur = pygame.transform.smoothscale(surface, (WIDTH // 10, HEIGHT // 10))
    blur = pygame.transform.smoothscale(blur, (WIDTH, HEIGHT))
    blur.set_alpha(190)
    surface.blit(blur, (0, 0))
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((42, 30, 24, 105))
    surface.blit(shade, (0, 0))

    accent = game.level.theme["edge"]
    panel = pygame.Rect(WIDTH // 2 - 330, 108, 660, 506)
    fx.draw_panel(surface, panel, accent, game.ui_t, radius=24)

    text(surface, "LEVEL COMPLETE", 38, INK, (panel.centerx, panel.y + 42),
         "center", bold=True)
    text(surface, game.level.name, 15, SOFT, (panel.centerx, panel.y + 80), "center")

    stars = game.stars
    for i in range(3):
        cx = panel.centerx + (i - 1) * 92
        cy = panel.y + 150
        filled = i < stars
        scale = 1.0 + (0.08 * math.sin(game.ui_t * 4 + i) if filled else 0.0)
        radius = int(26 * scale)
        points = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            r = radius if k % 2 == 0 else radius * 0.43
            points.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        if filled:
            pygame.draw.polygon(surface, (246, 194, 78), points)
            pygame.draw.polygon(surface, (166, 108, 34), points, 2)
        else:
            pygame.draw.polygon(surface, (206, 188, 168), points, 2)

    rows = (
        ("COINS", f"{game.level_coins} / {game.level.total_coins}", GOLD_INK),
        ("TIME", fmt_time(game.level.time), INK),
        ("DEATHS", str(game.deaths), NEON_PINK if game.deaths else NEON_GREEN),
    )
    for i, (label, value, color) in enumerate(rows):
        y = panel.y + 212 + i * 40
        text(surface, label, 15, MUTED, (panel.x + 100, y), "midleft", bold=True)
        text(surface, value, 21, color, (panel.right - 100, y), "midright", bold=True)
        pygame.draw.line(surface, DARK_LINE, (panel.x + 100, y + 20),
                         (panel.right - 100, y + 20), 1)
    if game.new_record:
        text(surface, "★ NEW BEST ★", 14, NEON_GOLD,
             (panel.centerx, panel.y + 336), "center", bold=True)
    else:
        record = game.save.record(game.level_index)
        if record:
            text(surface, f"best: {record['coins']}/{record['total']} coins · {fmt_time(record['time'])}",
                 12, MUTED, (panel.centerx, panel.y + 336), "center")

    labels = ("FINISH" if game.level_index >= 2 else "NEXT", "MAIN MENU")
    colors = (NEON_GREEN, (130, 118, 108))
    for i, label in enumerate(labels):
        rect = pygame.Rect(panel.x + 92 + i * 258, panel.y + 380, 218, 54)
        game.hotspots.append((rect, "complete", i))
        draw_button(surface, rect, label, game.complete_index == i, colors[i], 20,
                    game.ui_t)
    text(surface, "ENTER to confirm   ·   ESC for menu", 12, MUTED,
         (panel.centerx, panel.bottom - 26), "midbottom")


def draw_win(game, surface):
    blur = pygame.transform.smoothscale(surface, (WIDTH // 10, HEIGHT // 10))
    blur = pygame.transform.smoothscale(blur, (WIDTH, HEIGHT))
    blur.set_alpha(200)
    surface.blit(blur, (0, 0))
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((38, 28, 22, 110))
    surface.blit(shade, (0, 0))

    t = game.ui_t
    panel = pygame.Rect(WIDTH // 2 - 340, 76, 680, 570)
    border = game.backdrop.theme["edge"]
    fx.draw_panel(surface, panel, border, t, radius=26)

    text(surface, "YOU WIN!", 64, NEON_PINK, (panel.centerx, panel.y + 50),
         "center", bold=True)
    text(surface, "all three levels cleared. the spikes are jealous.", 15, SOFT,
         (panel.centerx, panel.y + 104), "center")

    pygame.draw.ellipse(surface, (198, 174, 148), (panel.centerx - 52, panel.y + 266, 104, 16))
    pygame.draw.ellipse(surface, (255, 250, 240), (panel.centerx - 46, panel.y + 263, 92, 12))
    player_mod.draw_character(
        surface, (panel.centerx, 296), (80, 100),
        PALETTES[game.save.equipped("skin")], hat=game.save.equipped("hat"),
        eyes=game.save.equipped("eyes"), facing=1, t=t,
        walk=math.sin(t * 5) * 0.6,
    )

    rows = (
        ("COINS COLLECTED", str(game.save.coins), GOLD_INK),
        ("DEATHS THIS RUN", str(game.session_deaths),
         NEON_PINK if game.session_deaths else NEON_GREEN),
        ("TOTAL TIME", fmt_time(game.session_time), INK),
        ("RATING", f"{game.total_stars} / 9", NEON_GOLD),
    )
    for i, (label, value, color) in enumerate(rows):
        y = panel.y + 320 + i * 34
        text(surface, label, 13, MUTED, (panel.x + 150, y), "midleft", bold=True)
        text(surface, value, 18, color, (panel.right - 150, y), "midright", bold=True)

    labels = ("PLAY AGAIN", "MAIN MENU")
    colors = (NEON_GREEN, (130, 118, 108))
    for i, label in enumerate(labels):
        rect = pygame.Rect(panel.centerx - 220 + i * 230, panel.y + 472, 210, 54)
        game.hotspots.append((rect, "win", i))
        draw_button(surface, rect, label, game.win_index == i, colors[i], 20, t)
    text(surface, "ENTER to choose   ·   ESC for menu   ·   \\ for cheats",
         12, MUTED, (panel.centerx, panel.bottom - 24), "midbottom")
