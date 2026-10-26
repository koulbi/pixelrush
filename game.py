"""Game loop, states, cheats and module wiring."""
import math
import random

import pygame

import fx
import ui
from audio import Audio
from config import (
    CATEGORIES, FIXED_DT, HEIGHT, NEON_CYAN, NEON_GOLD, NEON_GREEN,
    NEON_PINK, PALETTES, SOFT, TITLE, WIDTH,
)
from level import LEVELS, Level
from player import Player, draw_character
from save import Save

CHEAT_ITEMS = [
    {"id": "god", "name": "God Mode", "short": "GOD", "kind": "toggle",
     "desc": "Spikes and falls no longer hurt"},
    {"id": "inf_jump", "name": "Infinite Jump", "short": "JUMPS", "kind": "toggle",
     "desc": "Jump as many times as you like in mid-air"},
    {"id": "speed", "name": "Turbo Speed ×1.8", "short": "TURBO", "kind": "toggle",
     "desc": "Faster running and dashing"},
    {"id": "moon", "name": "Moon Gravity", "short": "MOON", "kind": "toggle",
     "desc": "Higher jumps and a slow fall"},
    {"id": "magnet", "name": "Coin Magnet", "short": "MAGNET", "kind": "toggle",
     "desc": "Coins fly straight to you"},
    {"id": "noclip", "name": "Noclip", "short": "NOCLIP", "kind": "toggle",
     "desc": "Fly with WASD or the arrow keys"},
    {"id": "slowmo", "name": "Slow-Mo ×0.5", "short": "SLOW-MO", "kind": "toggle",
     "desc": "Slows down game time"},
    {"id": "coins", "name": "+250 Coins", "short": "", "kind": "action",
     "desc": "Add 250 coins to your wallet"},
    {"id": "unlock", "name": "Unlock Everything", "short": "", "kind": "action",
     "desc": "Unlock every cosmetic item"},
    {"id": "skip", "name": "Skip Level", "short": "", "kind": "action",
     "desc": "Jump to the next level (in game only)"},
]

SETTINGS_ITEMS = [
    {"id": "fullscreen", "name": "Fullscreen",
     "desc": "Fill the whole screen with the game"},
    {"id": "sound", "name": "Sound",
     "desc": "Music and sound effects"},
    {"id": "screen_shake", "name": "Screen Shake",
     "desc": "Camera impact on deaths and landings"},
    {"id": "particles", "name": "Particles",
     "desc": "Sparkles, dust and celebration confetti"},
    {"id": "show_fps", "name": "Show FPS",
     "desc": "Show the frame rate in the corner of the HUD"},
]


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.save = Save()
        self.audio = Audio()
        self.audio.set_muted(self.save.data.get("muted", False))

        self.state = "menu"
        self.paused = False
        self.cheat_open = False
        self.cheat_index = 0
        self.cheat_items = CHEAT_ITEMS
        self.cheats = {item["id"]: False for item in CHEAT_ITEMS if item["kind"] == "toggle"}
        self.switch_anim = [0.0] * len(CHEAT_ITEMS)
        self.switch_targets = [0.0] * len(CHEAT_ITEMS)

        self.menu_index = 0
        self.pause_index = 0
        self.complete_index = 0
        self.win_index = 0
        self.settings_index = 0
        self.settings_items = SETTINGS_ITEMS
        self.settings_return = "menu"
        self.custom_cat = 0
        self.custom_return = "menu"
        self.custom_sel = [
            self.save.equipped("skin"),
            self.save.equipped("hat"),
            self.save.equipped("eyes"),
        ]

        self.backdrop = Level(LEVELS[0], 0)
        self.level = None
        self.player = None
        self.level_index = 0
        self.level_coins = 0
        self.deaths = 0
        self.stars = 0
        self.level_intro = 0
        self.respawn_point = (0, 0)
        self.new_record = False
        self.session_deaths = 0
        self.session_time = 0.0
        self.total_stars = 0

        self.camera = fx.Camera()
        self.particles = fx.Particles()
        self.overlay_particles = fx.Particles()
        self.toasts = []
        self.hotspots = []
        self.ui_t = 0.0
        self.acc = 0.0
        self.fps = 0.0
        self._fps_accum = 0.0
        self._fps_frames = 0

        if self.save.setting("fullscreen"):
            self.apply_display_mode()
        self._make_icon()

    # ------------------------------------------------------------------
    def _make_icon(self):
        try:
            icon = pygame.Surface((64, 64), pygame.SRCALPHA)
            draw_character(icon, (32, 38), (26, 32), PALETTES[0],
                           hat=1, eyes=0, facing=1, t=0.0)
            pygame.display.set_icon(icon)
        except pygame.error:
            pass

    def apply_display_mode(self):
        flags = (pygame.FULLSCREEN | pygame.SCALED) if self.save.setting("fullscreen") else 0
        try:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except pygame.error:
            self.save.set_setting("fullscreen", False)
            self.save.write()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)
        pygame.display.set_caption(TITLE)

    def add_shake(self, amount):
        if self.save.setting("screen_shake"):
            self.camera.add_shake(amount)

    # ------------------------------------------------------------------
    #  Состояния
    # ------------------------------------------------------------------
    def toast(self, message, color=NEON_CYAN):
        self.toasts.append({"text": message, "color": color, "timer": 120, "max": 120})
        self.toasts = self.toasts[-3:]

    def toggle_mute(self):
        muted = self.audio.toggle_mute()
        self.save.data["muted"] = muted
        self.save.write()
        self.toast("Sound off" if muted else "Sound on", SOFT)

    def open_settings(self):
        self.settings_return = "pause" if self.state == "play" and self.paused else "menu"
        self.state = "settings"
        self.settings_index = 0
        self.cheat_open = False
        self.audio.play("click")

    def close_settings(self):
        self.audio.play("click")
        if self.settings_return == "pause":
            self.state = "play"
            self.paused = True
        else:
            self.state = "menu"

    def settings_value(self, index):
        item = self.settings_items[index]
        if item["id"] == "sound":
            return not self.audio.muted
        return self.save.setting(item["id"])

    def toggle_setting(self, index):
        item = self.settings_items[index]
        setting_id = item["id"]
        self.audio.play("click")
        if setting_id == "sound":
            muted = self.audio.toggle_mute()
            self.save.data["muted"] = muted
            self.save.write()
            return
        if setting_id == "fullscreen":
            self.save.set_setting("fullscreen", not self.save.setting("fullscreen"))
            self.apply_display_mode()
            self.save.write()
            return
        value = not self.save.setting(setting_id)
        self.save.set_setting(setting_id, value)
        if setting_id == "screen_shake" and not value:
            self.camera.shake = 0.0
        elif setting_id == "particles" and not value:
            self.particles.clear()
            self.overlay_particles.clear()
        self.save.write()

    def open_customize(self):
        self.custom_return = "play" if self.state == "play" else "menu"
        if self.state == "play":
            self.paused = True
        self.custom_sel = [
            self.save.equipped("skin"),
            self.save.equipped("hat"),
            self.save.equipped("eyes"),
        ]
        self.custom_cat = 0
        self.state = "customize"
        self.cheat_open = False
        self.audio.play("click")

    def close_customize(self):
        self.audio.play("click")
        if self.custom_return == "play":
            self.state = "play"
            self.paused = True
        else:
            self.state = "menu"

    def apply_custom_item(self):
        cat = CATEGORIES[self.custom_cat]
        idx = self.custom_sel[self.custom_cat]
        item = cat["items"][idx]
        if self.save.is_unlocked(cat["key"], idx):
            self.save.equip(cat["equip"], idx)
            self.save.write()
            self.audio.play("click")
            self.toast(f"{item['name']} equipped", SOFT)
            return
        price = item["price"]
        if self.save.coins >= price:
            self.save.add_coins(-price)
            self.save.unlock(cat["key"], idx)
            self.save.equip(cat["equip"], idx)
            self.save.write()
            self.audio.play("buy")
            self.toast(f"Purchased: {item['name']} (−{price})", NEON_GOLD)
        else:
            self.audio.play("error")
            self.toast("Not enough coins — collect more!", NEON_PINK)

    def start_game(self):
        self.session_deaths = 0
        self.session_time = 0.0
        self.total_stars = 0
        self.audio.play("click")
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index
        self.level = Level(LEVELS[index], index)
        self.player = Player(*self.level.spawn)
        self.level_coins = 0
        self.deaths = 0
        self.stars = 0
        self.new_record = False
        self.respawn_point = self.level.spawn
        self.camera = fx.Camera()
        self.camera.snap(self.player.rect.centerx, self.level.width)
        self.particles.clear()
        record = self.save.record(index)
        if record and record.get("total") != self.level.total_coins:
            record["total"] = self.level.total_coins
            record["coins"] = min(int(record.get("coins", 0)), self.level.total_coins)
            self.save.write()
        self.level_intro = 130
        self.acc = 0.0
        self.paused = False
        self.cheat_open = False
        self.state = "play"

    def restart_level(self):
        self.load_level(self.level_index)
        self.audio.play("click")

    def next_level(self):
        if self.level_index + 1 < len(LEVELS):
            self.load_level(self.level_index + 1)
        else:
            self.go_win()

    def go_menu(self):
        self.state = "menu"
        self.paused = False
        self.cheat_open = False
        self.particles.clear()
        self.overlay_particles.clear()
        self.save.write()
        self.audio.play("click")

    def go_win(self):
        self.state = "win"
        self.win_index = 0
        self.paused = False
        self.cheat_open = False
        self.audio.play("win")
        self.overlay_particles.confetti(90)
        self.save.write()

    # ------------------------------------------------------------------
    #  Смерть / монеты / финиш
    # ------------------------------------------------------------------
    def kill_player(self, cause):
        if self.state != "play" or self.player is None or self.player.dead:
            return
        if self.cheats["noclip"]:
            return
        if self.cheats["god"]:
            if cause == "fall":
                self.respawn_player(soft=True)
                self.toast("God mode: teleported to checkpoint", NEON_GREEN)
            return
        if self.player.invuln > 0:
            return
        self.player.kill()
        self.deaths += 1
        self.session_deaths += 1
        self.audio.play("death")
        self.add_shake(14)
        palette = PALETTES[self.save.equipped("skin")]
        cx, cy = self.player.rect.center
        self.particles.burst(cx, cy, palette["body"], 22, (1.5, 7), (22, 44), (2, 6), gravity=0.22)
        self.particles.stars(cx, cy, palette["accent"], 14, (1, 6), (20, 40), (3, 7))
        self.particles.text_pop(cx, cy - 26, "OUCH!", (214, 92, 88), 20, 40)

    def respawn_player(self, soft=False):
        x, y = self.respawn_point
        self.player.respawn_at(x, y)
        self.camera.snap(self.player.rect.centerx, self.level.width)
        if not soft:
            palette = PALETTES[self.save.equipped("skin")]
            self.particles.stars(self.player.rect.centerx, self.player.rect.centery,
                                 palette["accent"], 14, (1, 5), (18, 34), (2, 5))

    def update_coins(self):
        if self.player.dead:
            return
        player = self.player
        prect = player.rect.inflate(18, 18)
        pcenter = player.rect.center
        magnet = self.cheats["magnet"]
        for coin in self.level.coins:
            if coin.collected:
                continue
            if magnet:
                dx = pcenter[0] - coin.x
                dy = pcenter[1] - coin.y
                dist = math.hypot(dx, dy)
                if dist < 380 and dist > 1:
                    coin.attracted = True
                    speed = 3.5 + (380 - dist) * 0.05
                    coin.x += dx / dist * min(12.0, speed)
                    coin.y += dy / dist * min(12.0, speed)
                    if random.random() < 0.3:
                        self.particles.add(fx.Particle(
                            coin.x, coin.y, random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6),
                        12, (255, 220, 120), 2, kind="star"))
            if prect.collidepoint(coin.x, coin.y):
                coin.collected = True
                self.level.coins_collected += 1
                self.level_coins += 1
                self.save.add_coins(1)
                self.audio.play("coin")
                self.particles.stars(coin.x, coin.y, (255, 215, 90), 9, (1, 4), (16, 30), (2, 5))
                self.particles.text_pop(coin.x, coin.y - 16, "+1", (255, 225, 120), 16, 38)

    def check_checkpoints(self):
        if self.player.dead:
            return
        for cp in self.level.checkpoints:
            if self.player.rect.colliderect(cp.rect):
                was_active = cp.active
                cp.active = True
                if self.respawn_point != cp.respawn:
                    self.respawn_point = cp.respawn
                if not was_active:
                    self.audio.play("checkpoint")
                    self.particles.stars(cp.x, cp.y - 50, self.level.theme["edge"],
                                         12, (1, 4), (20, 40), (2, 5))
                    self.toast("Checkpoint reached", self.level.theme["edge"])

    def complete_level(self):
        if self.state != "play":
            return
        self.state = "complete"
        self.complete_index = 0
        self.level_intro = 0
        ratio = self.level_coins / max(1, self.level.total_coins)
        self.stars = 3 if ratio >= 0.999 else 2 if ratio >= 0.65 else 1
        self.total_stars += self.stars
        self.new_record = self.save.update_record(
            self.level_index, self.level.time, self.level_coins,
            self.deaths, self.level.total_coins,
        )
        self.save.write()
        self.audio.play("win")
        self.add_shake(6)
        self.overlay_particles.confetti(55)
        palette = PALETTES[self.save.equipped("skin")]
        self.particles.stars(self.player.rect.centerx, self.player.rect.centery - 20,
                             palette["accent"], 26, (2, 8), (30, 60), (2, 6))

    # ------------------------------------------------------------------
    #  Читы
    # ------------------------------------------------------------------
    def toggle_cheat(self, index):
        item = self.cheat_items[index]
        self.audio.play("click")
        if item["kind"] == "toggle":
            cheat_id = item["id"]
            value = not self.cheats.get(cheat_id, False)
            self.cheats[cheat_id] = value
            self.switch_targets[index] = 1.0 if value else 0.0
            self.toast(f"{item['name']}: {'ON' if value else 'OFF'}",
                       NEON_GREEN if value else SOFT)
            if cheat_id == "noclip" and value:
                self.player.vx = self.player.vy = 0.0
        elif item["id"] == "coins":
            self.save.add_coins(250)
            self.save.write()
            self.audio.play("buy")
            self.toast("+250 coins added", NEON_GOLD)
        elif item["id"] == "unlock":
            for cat in CATEGORIES:
                for i in range(len(cat["items"])):
                    self.save.unlock(cat["key"], i)
            self.save.write()
            self.audio.play("buy")
            self.toast("Every cosmetic unlocked!", NEON_GOLD)
        elif item["id"] == "skip":
            if self.state == "play":
                self.cheat_open = False
                self.paused = False
                self.next_level()
            else:
                self.audio.play("error")
                self.toast("Skip is only available while playing", NEON_PINK)

    def close_cheats(self):
        self.cheat_open = False
        self.audio.play("click")

    # ------------------------------------------------------------------
    #  События
    # ------------------------------------------------------------------
    @staticmethod
    def _is_cheat_key(event):
        if event.key == pygame.K_BACKSLASH:
            return True
        if getattr(event, "scancode", None) == 49:
            return True
        return getattr(event, "unicode", "") == "\\"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.toggle_mute()
                return
            if self._is_cheat_key(event):
                self.cheat_open = not self.cheat_open
                self.audio.play("click")
                if self.cheat_open:
                    self.cheat_index = 0
                return
            if self.cheat_open:
                self._cheat_keydown(event)
                return
            self._state_keydown(event)
        elif event.type == pygame.MOUSEMOTION:
            if self.cheat_open:
                self._cheat_hover(event.pos)
            elif self.state == "menu":
                self._menu_hover(event.pos)
            elif self.state == "settings":
                self._settings_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)
        elif event.type == pygame.MOUSEWHEEL and self.cheat_open:
            self.cheat_index = (self.cheat_index - event.y) % len(self.cheat_items)

    def _cheat_hover(self, pos):
        panel = ui.CHEAT_RECT
        if not panel.collidepoint(pos):
            return
        rows_top = panel.y + 76
        for i in range(len(self.cheat_items)):
            row = pygame.Rect(panel.x + 16, rows_top + i * 33, panel.w - 32, 30)
            if row.collidepoint(pos):
                self.cheat_index = i
                return

    def _menu_hover(self, pos):
        for i in range(4):
            rect = pygame.Rect(WIDTH // 2 - 170, 300 + i * 68, 340, 56)
            if rect.collidepoint(pos):
                self.menu_index = i
                return

    def _settings_hover(self, pos):
        panel = ui.SETTINGS_RECT
        rows_top = panel.y + 22
        for i in range(len(self.settings_items)):
            row = pygame.Rect(panel.x + 24, rows_top + i * 54, panel.w - 48, 44)
            if row.collidepoint(pos):
                self.settings_index = i
                return

    def _cheat_keydown(self, event):
        key = event.key
        if key in (pygame.K_UP, pygame.K_w):
            self.cheat_index = (self.cheat_index - 1) % len(self.cheat_items)
            self.audio.play("click")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.cheat_index = (self.cheat_index + 1) % len(self.cheat_items)
            self.audio.play("click")
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.toggle_cheat(self.cheat_index)
        elif key == pygame.K_ESCAPE:
            self.close_cheats()

    def _state_keydown(self, event):
        key = event.key
        confirm = key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)

        if self.state == "menu":
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % 4
                self.audio.play("click")
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % 4
                self.audio.play("click")
            elif confirm:
                self._activate_menu()

        elif self.state == "customize":
            cat = CATEGORIES[self.custom_cat]
            if key in (pygame.K_UP, pygame.K_w):
                self.custom_cat = (self.custom_cat - 1) % len(CATEGORIES)
                self.audio.play("click")
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.custom_cat = (self.custom_cat + 1) % len(CATEGORIES)
                self.audio.play("click")
            elif key in (pygame.K_LEFT, pygame.K_a):
                n = len(cat["items"])
                self.custom_sel[self.custom_cat] = (self.custom_sel[self.custom_cat] - 1) % n
                self.audio.play("click")
            elif key in (pygame.K_RIGHT, pygame.K_d):
                n = len(cat["items"])
                self.custom_sel[self.custom_cat] = (self.custom_sel[self.custom_cat] + 1) % n
                self.audio.play("click")
            elif confirm:
                self.apply_custom_item()
            elif key == pygame.K_ESCAPE:
                self.close_customize()

        elif self.state == "settings":
            if key in (pygame.K_UP, pygame.K_w):
                self.settings_index = (self.settings_index - 1) % len(self.settings_items)
                self.audio.play("click")
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.settings_index = (self.settings_index + 1) % len(self.settings_items)
                self.audio.play("click")
            elif confirm:
                self.toggle_setting(self.settings_index)
            elif key == pygame.K_ESCAPE:
                self.close_settings()

        elif self.state == "play":
            if self.paused:
                if key in (pygame.K_UP, pygame.K_w):
                    self.pause_index = (self.pause_index - 1) % 5
                    self.audio.play("click")
                elif key in (pygame.K_DOWN, pygame.K_s):
                    self.pause_index = (self.pause_index + 1) % 5
                    self.audio.play("click")
                elif confirm:
                    self._exec_pause(self.pause_index)
                elif key == pygame.K_ESCAPE:
                    self.paused = False
                    self.audio.play("click")
            else:
                if key == pygame.K_ESCAPE:
                    self.paused = True
                    self.pause_index = 0
                    self.audio.play("click")
                elif key == pygame.K_r:
                    self.restart_level()
                elif key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP, pygame.K_z):
                    self.player.request_jump()
                elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.player.request_dash()

        elif self.state == "complete":
            if key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                self.complete_index = (self.complete_index - 1) % 2
                self.audio.play("click")
            elif key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                self.complete_index = (self.complete_index + 1) % 2
                self.audio.play("click")
            elif confirm:
                self._exec_complete(self.complete_index)
            elif key == pygame.K_ESCAPE:
                self.go_menu()

        elif self.state == "win":
            if key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                self.win_index = (self.win_index - 1) % 2
                self.audio.play("click")
            elif key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                self.win_index = (self.win_index + 1) % 2
                self.audio.play("click")
            elif confirm:
                self._exec_win(self.win_index)
            elif key == pygame.K_ESCAPE:
                self.go_menu()

    def _activate_menu(self):
        if self.menu_index == 0:
            self.start_game()
        elif self.menu_index == 1:
            self.open_customize()
        elif self.menu_index == 2:
            self.open_settings()
        else:
            self.save.write()
            self.running = False

    def _exec_pause(self, index):
        if index == 0:
            self.paused = False
            self.audio.play("click")
        elif index == 1:
            self.restart_level()
        elif index == 2:
            self.open_customize()
        elif index == 3:
            self.open_settings()
        else:
            self.go_menu()

    def _exec_complete(self, index):
        if index == 0:
            self.audio.play("click")
            self.next_level()
        else:
            self.go_menu()

    def _exec_win(self, index):
        if index == 0:
            self.start_game()
        else:
            self.go_menu()

    def _click(self, pos):
        if self.cheat_open:
            for rect, kind, payload in reversed(self.hotspots):
                if kind.startswith("cheat") and rect.collidepoint(pos):
                    if kind == "cheat_row":
                        self.cheat_index = payload
                        self.toggle_cheat(payload)
                    elif kind == "cheat_close":
                        self.close_cheats()
                    return
            if not ui.CHEAT_RECT.collidepoint(pos):
                self.close_cheats()
            return

        for rect, kind, payload in reversed(self.hotspots):
            if not rect.collidepoint(pos):
                continue
            if kind == "menu":
                self.menu_index = payload
                self._activate_menu()
            elif kind == "custom_item":
                ci, idx = payload
                if self.custom_cat != ci or self.custom_sel[ci] != idx:
                    self.custom_cat = ci
                    self.custom_sel[ci] = idx
                    self.audio.play("click")
                else:
                    self.apply_custom_item()
            elif kind == "custom_back":
                self.close_customize()
            elif kind == "custom_play":
                self.save.write()
                self.start_game()
            elif kind == "setting":
                self.settings_index = payload
                self.toggle_setting(payload)
            elif kind == "settings_back":
                self.close_settings()
            elif kind == "cheat_open":
                self.cheat_open = True
                self.cheat_index = 0
                self.audio.play("click")
            elif kind == "pause":
                self.pause_index = payload
                self._exec_pause(payload)
            elif kind == "complete":
                self.complete_index = payload
                self._exec_complete(payload)
            elif kind == "win":
                self.win_index = payload
                self._exec_win(payload)
            return

    # ------------------------------------------------------------------
    #  Обновление
    # ------------------------------------------------------------------
    def update(self, dt):
        dt = min(dt, 0.05)
        self.ui_t += dt
        self._fps_accum += dt
        self._fps_frames += 1
        if self._fps_accum >= 0.4:
            self.fps = self._fps_frames / self._fps_accum
            self._fps_accum = 0.0
            self._fps_frames = 0

        for toast in self.toasts:
            toast["timer"] -= 1
        self.toasts = [toast for toast in self.toasts if toast["timer"] > 0]

        for i in range(len(self.cheat_items)):
            self.switch_anim[i] += (self.switch_targets[i] - self.switch_anim[i]) * min(1.0, dt * 14)

        if self.save.setting("particles"):
            if not self.paused and not self.cheat_open:
                self.particles.update()
            if self.state in ("complete", "win"):
                self.overlay_particles.update()
                if self.state == "win" and random.random() < 0.18:
                    self.overlay_particles.confetti(1)
        else:
            self.particles.clear()
            self.overlay_particles.clear()

        if self.state != "play":
            return
        if self.paused or self.cheat_open:
            return

        scale = 0.5 if self.cheats["slowmo"] else 1.0
        self.acc += dt * scale
        steps = 0
        while self.acc >= FIXED_DT and steps < 4:
            self.step()
            self.acc -= FIXED_DT
            steps += 1

    def step(self):
        level = self.level
        player = self.player
        if level is None or player is None:
            return

        if self.level_intro > 0:
            self.level_intro -= 1

        level.update()
        keys = pygame.key.get_pressed()
        player.update(self, keys)
        self.update_coins()

        if not player.dead:
            hitbox = player.rect.inflate(-9, -7)
            for spike in level.spikes:
                if hitbox.colliderect(spike.hitbox):
                    self.kill_player("spike")
                    break
        self.check_checkpoints()

        if not player.dead and player.rect.colliderect(level.goal.rect):
            self.complete_level()
            return

        if player.dead and player.dead_timer <= 0:
            self.respawn_player()

        self.camera.update(player.rect.centerx, level.width, look_ahead=player.vx * 7)
        self.session_time += FIXED_DT

        # portal sparks (optional effects)
        if self.save.setting("particles") and random.random() < 0.35:
            goal = level.goal
            color = random.choice((level.theme["edge"], (255, 255, 255), level.theme["accent"]))
            self.particles.add(fx.Particle(
                goal.x + random.uniform(-26, 26), goal.y - random.uniform(40, 112),
                random.uniform(-0.4, 0.4), random.uniform(-1.4, -0.4),
                random.randint(28, 55), color, random.uniform(1.5, 3.5),
                gravity=-0.01, kind="star"))

    # ------------------------------------------------------------------
    #  Отрисовка
    # ------------------------------------------------------------------
    def draw(self, surface):
        self.hotspots = []
        if self.state == "menu":
            ui.draw_menu(self, surface)
        elif self.state == "customize":
            ui.draw_customize(self, surface)
        elif self.state == "settings":
            ui.draw_settings(self, surface)
        elif self.state == "play":
            self.draw_world(surface)
            ui.draw_hud(self, surface)
            ui.draw_level_intro(self, surface)
            if self.paused:
                ui.draw_pause(self, surface)
        elif self.state == "complete":
            self.draw_world(surface, hud=False)
            if self.save.setting("particles"):
                self.overlay_particles.draw(surface, (0, 0))
            ui.draw_complete(self, surface)
        elif self.state == "win":
            self.draw_world(surface, hud=False)
            if self.save.setting("particles"):
                self.overlay_particles.draw(surface, (0, 0))
            ui.draw_win(self, surface)

        if self.state in ("menu", "customize", "settings") or (self.state == "play" and not self.paused):
            ui.draw_toasts(self, surface)
        if self.cheat_open:
            ui.draw_cheats(self, surface)

    def draw_world(self, surface, hud=True):
        level = self.level
        if level is None:
            return
        level.draw_background(surface, self.camera.x, level.clock)
        if self.state == "play" and not self.paused and not self.cheat_open:
            sx, sy = self.camera.offset()
        else:
            sx, sy = 0, 0
        offset = (int(self.camera.x) + sx, sy)
        level.draw(surface, offset, level.clock)
        if self.save.setting("particles"):
            self.particles.draw(surface, offset)
        if self.player is not None:
            self.player.draw(surface, offset, self.save, self.ui_t)
        level.draw_foreground(surface, offset, level.clock)

    # ------------------------------------------------------------------
    def shutdown(self):
        self.save.write()
        if self.audio.enabled:
            pygame.mixer.stop()
