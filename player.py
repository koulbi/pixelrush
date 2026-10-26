"""Player: physics, jumping, dashing and character art."""
import math

import pygame

import fx
from config import (
    ACCEL, AIR_ACCEL, COYOTE_TIME, DASH_COOLDOWN, DASH_SPEED, DASH_TIME,
    DOUBLE_JUMP_VEL, FRICTION, GRAVITY, JUMP_BUFFER, JUMP_VEL, MAX_FALL,
    MAX_SPEED, PALETTES, PLAYER_H, PLAYER_W,
)


# ---------------------------------------------------------------------------
#  Отрисовка персонажа (используется и в гардеробе)
# ---------------------------------------------------------------------------
def _star_polygon(cx, cy, radius, inner=0.42, points=4):
    result = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        r = radius if i % 2 == 0 else radius * inner
        result.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return result


def _draw_hat(surface, cx, cy, w, h, hat, accent, body, t):
    top = cy - h / 2

    if hat == 1:  # кепка
        dome = pygame.Rect(cx - w * 0.46, top - h * 0.20, w * 0.92, h * 0.34)
        pygame.draw.ellipse(surface, fx.mix(accent, (0, 0, 0), 0.25), dome)
        pygame.draw.ellipse(surface, accent, dome.inflate(-4, -4))
        brim = pygame.Rect(cx - w * 0.18, top + h * 0.02, w * 0.86, h * 0.11)
        pygame.draw.rect(surface, fx.mix(accent, (0, 0, 0), 0.4), brim, border_radius=4)
        pygame.draw.circle(surface, fx.mix(accent, (255, 255, 255), 0.5),
                           (int(cx), int(top - h * 0.16)), max(2, int(w * 0.06)))

    elif hat == 2:  # наушники
        band = pygame.Rect(cx - w * 0.58, top - h * 0.24, w * 1.16, h * 0.72)
        pygame.draw.arc(surface, fx.mix(accent, (0, 0, 0), 0.1), band, 0.05, math.pi - 0.05, 5)
        for side in (-1, 1):
            px = cx + side * w * 0.5
            py = top + h * 0.18
            pygame.draw.circle(surface, (74, 52, 38), (int(px), int(py)), int(w * 0.15))
            pygame.draw.circle(surface, accent, (int(px), int(py)), int(w * 0.15), 3)
            pygame.draw.circle(surface, fx.mix(accent, (255, 255, 255), 0.4),
                               (int(px), int(py)), int(w * 0.055))

    elif hat == 3:  # рога
        for side in (-1, 1):
            base_x = cx + side * w * 0.3
            pygame.draw.polygon(surface, (222, 112, 86), [
                (base_x - w * 0.11, top + h * 0.03),
                (base_x + w * 0.11, top + h * 0.03),
                (base_x + side * w * 0.22, top - h * 0.34),
            ])
            pygame.draw.polygon(surface, (126, 62, 48), [
                (base_x - w * 0.11, top + h * 0.03),
                (base_x + w * 0.11, top + h * 0.03),
                (base_x + side * w * 0.22, top - h * 0.34),
            ], 2)

    elif hat == 4:  # корона
        pts = [
            (cx - w * 0.4, top + h * 0.04),
            (cx - w * 0.42, top - h * 0.22),
            (cx - w * 0.22, top - h * 0.04),
            (cx - w * 0.08, top - h * 0.28),
            (cx + w * 0.08, top - h * 0.28),
            (cx + w * 0.22, top - h * 0.04),
            (cx + w * 0.42, top - h * 0.22),
            (cx + w * 0.4, top + h * 0.04),
        ]
        pygame.draw.polygon(surface, (255, 206, 70), pts)
        pygame.draw.polygon(surface, (255, 240, 160), pts, 2)
        pygame.draw.rect(surface, (255, 180, 40), (cx - w * 0.4, top - h * 0.01, w * 0.8, h * 0.08))
        for dx, color in ((-w * 0.18, accent), (0, (255, 250, 240)), (w * 0.18, accent)):
            pygame.draw.circle(surface, color, (int(cx + dx), int(top + h * 0.02)), max(2, int(w * 0.05)))

    elif hat == 5:  # колпак
        pygame.draw.polygon(surface, (72, 145, 146), [
            (cx - w * 0.38, top + h * 0.05),
            (cx + w * 0.38, top + h * 0.05),
            (cx + w * 0.12, top - h * 0.55),
        ])
        pygame.draw.polygon(surface, (124, 192, 192), [
            (cx - w * 0.38, top + h * 0.05),
            (cx + w * 0.38, top + h * 0.05),
            (cx + w * 0.12, top - h * 0.55),
        ], 2)
        brim = pygame.Rect(cx - w * 0.52, top + h * 0.02, w * 1.04, h * 0.13)
        pygame.draw.ellipse(surface, (54, 112, 114), brim)
        pygame.draw.ellipse(surface, (98, 166, 166), brim, 2)
        for dx, dy in ((-w * 0.12, -h * 0.14), (w * 0.16, -h * 0.3), (0, -h * 0.44)):
            pygame.draw.circle(surface, (255, 214, 90), (int(cx + dx), int(top + dy)), 2)

    elif hat == 6:  # halo
        halo = pygame.Rect(cx - w * 0.36, top - h * 0.38, w * 0.72, h * 0.12)
        for i in range(3):
            pygame.draw.ellipse(surface, (245, 196, 86),
                                halo.inflate(i * 4, i * 4), 1)
        pygame.draw.ellipse(surface, (255, 226, 150), halo, 3)
        for i in range(5):
            ang = t * 2 + i * math.tau / 5
            px = cx + math.cos(ang) * w * 0.4
            py = top - h * 0.32 + math.sin(ang) * h * 0.03
            pygame.draw.circle(surface, (255, 246, 210), (int(px), int(py)), 1)

    elif hat == 7:  # beret
        brim = pygame.Rect(int(cx - w * 0.5), int(top + h * 0.02), int(w * 1.0), int(h * 0.1))
        pygame.draw.ellipse(surface, fx.mix(accent, (0, 0, 0), 0.32), brim)
        dome = pygame.Rect(int(cx - w * 0.43), int(top - h * 0.14), int(w * 0.86), int(h * 0.27))
        pygame.draw.ellipse(surface, fx.mix(accent, (0, 0, 0), 0.25), dome.inflate(4, 4))
        pygame.draw.ellipse(surface, accent, dome)
        pygame.draw.ellipse(surface, fx.mix(accent, (255, 252, 245), 0.24),
                           dome.inflate(-int(w * 0.14), -int(h * 0.08)))
        pygame.draw.circle(surface, fx.mix(accent, (0, 0, 0), 0.38),
                           (int(cx + w * 0.18), int(top - h * 0.15)), max(2, int(w * 0.05)))

    elif hat == 8:  # flower
        flower_x = cx + w * 0.06
        flower_y = top - h * 0.18
        petal = max(3, int(w * 0.085))
        for i in range(6):
            ang = i * math.tau / 6 + 0.25
            px = flower_x + math.cos(ang) * w * 0.15
            py = flower_y + math.sin(ang) * h * 0.11
            pygame.draw.circle(surface, (255, 238, 196), (int(px), int(py)), petal + 1)
            pygame.draw.circle(surface, accent, (int(px), int(py)), petal)
        pygame.draw.circle(surface, (245, 190, 72), (int(flower_x), int(flower_y)), max(2, petal - 1))
        pygame.draw.circle(surface, (255, 226, 140), (int(flower_x), int(flower_y)), max(1, petal - 3))


def _draw_eyes(surface, cx, cy, w, h, style, facing, t, blink):
    eye_y = cy - h * 0.06
    eye_dx = w * 0.2
    ew = max(3, int(w * 0.15))
    eh = max(4, int(h * 0.17))
    pupil_x = facing * ew * 0.3

    if style == 3:  # glasses
        glasses = pygame.Rect(int(cx - w * 0.38), int(eye_y - h * 0.09), int(w * 0.76), int(h * 0.2))
        pygame.draw.rect(surface, (54, 38, 30), glasses, border_radius=5)
        pygame.draw.rect(surface, (255, 252, 245), glasses, 2, border_radius=5)
        pygame.draw.line(surface, (222, 158, 56), (glasses.x + 4, glasses.y + 3),
                         (glasses.centerx - 2, glasses.y + 3), 2)

    if style != 3:
        for side in (-1, 1):
            ex = cx + side * eye_dx
            if style == 1 or (style == 5 and side == 1):  # happy / wink
                rect = pygame.Rect(int(ex - ew), int(eye_y - eh * 0.4), ew * 2, eh * 1.4)
                pygame.draw.arc(surface, (38, 28, 24), rect, 0.2, math.pi - 0.2, 3)
                continue
            if style == 4:  # stars
                pygame.draw.polygon(surface, (222, 158, 56), _star_polygon(ex, eye_y, ew * 1.25))
                pygame.draw.polygon(surface, (255, 246, 220), _star_polygon(ex, eye_y, ew * 0.7))
                continue
            if blink:
                pygame.draw.line(surface, (38, 28, 24), (ex - ew * 0.7, eye_y),
                                 (ex + ew * 0.7, eye_y), 3)
                continue
            pygame.draw.ellipse(surface, (255, 252, 245), (ex - ew, eye_y - eh, ew * 2, eh * 2))
            pygame.draw.ellipse(surface, (45, 34, 28), (ex - ew, eye_y - eh, ew * 2, eh * 2), 1)
            pygame.draw.circle(surface, (45, 34, 28),
                               (int(ex + pupil_x), int(eye_y + eh * 0.15)), max(2, int(ew * 0.45)))
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(ex + pupil_x - ew * 0.17), int(eye_y - eh * 0.15)), 1)
            if style == 2:  # angry brows
                pygame.draw.line(surface, (38, 28, 24),
                                 (ex - ew * 0.7, eye_y - eh * 1.4),
                                 (ex + ew * 0.7, eye_y - eh * 0.85), 3)
            elif style == 6:  # sleepy lids
                lid = pygame.Rect(int(ex - ew * 0.9), int(eye_y - eh * 0.55), ew * 2, eh * 1.1)
                pygame.draw.ellipse(surface, fx.mix((238, 170, 140), (255, 252, 245), 0.35), lid)
                pygame.draw.line(surface, (38, 28, 24),
                                 (ex - ew, eye_y - eh * 0.25), (ex + ew, eye_y - eh * 0.25), 3)

    # mouth
    mouth = pygame.Rect(int(cx - w * 0.1), int(cy + h * 0.16), int(w * 0.2), int(h * 0.09))
    if blink or style in (1, 5):
        pygame.draw.arc(surface, (38, 28, 24), mouth, 1.15, math.pi - 1.15, 2)
    else:
        pygame.draw.line(surface, (38, 28, 24),
                         (mouth.x, mouth.y), (mouth.right, mouth.y), 2)


def draw_character(surface, center, size, palette, hat=0, eyes=0,
                   facing=1, t=0.0, squash=1.0, alpha=255, walk=0.0):
    """Draw a simple head-and-limbs character anchored at center."""
    w, h = size
    cw = int(max(w * 3.2, 100))
    ch = int(max(h * 3.2, 120))
    canvas = pygame.Surface((cw, ch), pygame.SRCALPHA)
    cx, cy = cw / 2, ch * 0.62

    body = palette["body"]
    accent = palette["accent"]
    outline = fx.mix(body, (52, 38, 30), 0.62)

    # Head, torso and limb proportions. The shoes end exactly at cy + h / 2,
    # which is the player's hitbox bottom.
    head_w = w * 0.80
    head_h = h * 0.52
    head_cy = cy - h * 0.235
    head = pygame.Rect(cx - head_w / 2, head_cy - head_h / 2, head_w, head_h)
    torso_w = w * 0.44
    torso_top = head.bottom - h * 0.02
    torso_bottom = cy + h * 0.19
    torso = pygame.Rect(cx - torso_w / 2, torso_top, torso_w, torso_bottom - torso_top)
    hip_y = torso_bottom - h * 0.03
    foot_y = cy + h / 2
    limb_w = max(3, int(w * 0.10))
    swing = walk * w * 0.10

    def limb(a, b, color, width, end_color=None, end_r=None):
        pygame.draw.line(canvas, outline, a, b, width + 2)
        pygame.draw.line(canvas, color, a, b, width)
        if end_color is not None:
            pygame.draw.circle(canvas, outline, b, end_r + 1)
            pygame.draw.circle(canvas, end_color, b, end_r)

    # Legs and shoes.
    for side in (-1, 1):
        hip_x = cx + side * torso_w * 0.30
        foot_x = cx + side * w * 0.16 - side * swing
        limb((hip_x, hip_y), (foot_x, foot_y - h * 0.02), body, limb_w)
        shoe = pygame.Rect(0, 0, w * 0.21, h * 0.075)
        shoe.midbottom = (foot_x, foot_y)
        outline_shoe = pygame.Rect(shoe.x - 1, shoe.y - 1, shoe.w + 2, shoe.h + 1)
        pygame.draw.ellipse(canvas, outline, outline_shoe)
        pygame.draw.ellipse(canvas, accent, shoe)

    # Arms and hands.
    for side in (-1, 1):
        shoulder = (cx + side * (torso_w / 2 + w * 0.02), torso_top + h * 0.05)
        hand = (shoulder[0] + side * w * 0.08,
                shoulder[1] + h * 0.18 + side * swing * 0.35)
        limb(shoulder, hand, body, limb_w,
             accent, max(2, int(limb_w * 0.55)))

    # Torso.
    pygame.draw.rect(canvas, outline, torso.inflate(2, 2), border_radius=int(w * 0.14))
    pygame.draw.rect(canvas, accent, torso, border_radius=int(w * 0.13))

    # Head.
    pygame.draw.ellipse(canvas, outline, head.inflate(4, 4))
    pygame.draw.ellipse(canvas, body, head)

    # Face and hat.
    blink = (t % 4.4) > 4.22
    _draw_eyes(canvas, cx, head_cy, head_w, head_h, eyes, facing, t, blink)
    _draw_hat(canvas, cx, head_cy, head_w, head_h, hat, accent, body, t)

    if squash != 1.0:
        new_w = max(1, int(canvas.get_width() * (1 + (1 - squash) * 0.28)))
        new_h = max(1, int(canvas.get_height() * squash))
        canvas = pygame.transform.smoothscale(canvas, (new_w, new_h))
    if alpha < 255:
        canvas.set_alpha(alpha)
    # Anchor the character so the shoes sit exactly on the surface.
    surface.blit(canvas, (int(center[0] - canvas.get_width() / 2),
                          int(center[1] - canvas.get_height() * 0.62)))


# ---------------------------------------------------------------------------
#  Игрок
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x), int(y), PLAYER_W, PLAYER_H)
        self.x = float(x)
        self.y = float(y)
        self.spawn = (float(x), float(y))
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1
        self.on_ground = False
        self.standing_on = None
        self.jumps = 0
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.dash_timer = 0
        self.dash_cd = 0
        self.dash_dir = 1
        self.dash_request = False
        self.can_air_dash = True
        self.dead = False
        self.dead_timer = 0
        self.invuln = 0
        self.squash = 1.0
        self.walk_phase = 0.0
        self.t = 0.0

    # --- управление из событий ------------------------------------------
    def request_jump(self):
        if not self.dead:
            self.jump_buffer = JUMP_BUFFER * 60 + 2

    def request_dash(self):
        if not self.dead:
            self.dash_request = True

    # --- жизнь и смерть --------------------------------------------------
    def respawn_at(self, x, y):
        self.rect.topleft = (int(x), int(y))
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.standing_on = None
        self.jumps = 0
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.dash_timer = 0
        self.dash_cd = 0
        self.dead = False
        self.dead_timer = 0
        self.invuln = 70
        self.squash = 0.85

    def kill(self):
        self.dead = True
        self.dead_timer = 44
        self.vx = 0.0
        self.vy = 0.0

    # --- физика ----------------------------------------------------------
    def update(self, game, keys):
        if self.dead:
            self.dead_timer -= 1
            return

        self.t += 1.0 / 60.0
        self.walk_phase = math.sin(self.t * 15) * (1 if abs(self.vx) > 0.7 else 0)
        if self.invuln > 0:
            self.invuln -= 1
        if self.dash_cd > 0:
            self.dash_cd -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        level = game.level
        cheats = game.cheats
        palette = PALETTES[game.save.equipped("skin")]
        body_color = palette["body"]
        accent = palette["accent"]

        # движущаяся платформа несёт игрока
        if self.standing_on is not None and getattr(self.standing_on, "moving", False):
            platform = self.standing_on
            self.x += platform.delta[0]
            self.y += platform.delta[1]
            self.rect.x = round(self.x)
            self.rect.bottom = platform.rect.top
            self.x = float(self.rect.x)
            self.y = float(self.rect.y)

        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        axis = int(right) - int(left)
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        speed_mult = 1.8 if cheats["speed"] else 1.0

        if cheats["noclip"]:
            up = keys[pygame.K_w] or keys[pygame.K_UP]
            down = keys[pygame.K_s] or keys[pygame.K_DOWN]
            nx = (int(right) - int(left)) * 8.0 * speed_mult
            ny = (int(down) - int(up)) * 8.0 * speed_mult
            self.x += nx
            self.y += ny
            self.rect.x = round(self.x)
            self.rect.y = round(self.y)
            self.vx = nx
            self.vy = ny
            self.on_ground = False
            self.standing_on = None
            if axis:
                self.facing = axis
            if nx or ny:
                game.particles.add(fx.Particle(
                    self.rect.centerx, self.rect.centery, 0, 0, 12,
                    (255, 255, 255), 3, kind="dot"))
            return

        # рывок
        if self.dash_request:
            self.dash_request = False
            if self.dash_cd <= 0 and (self.on_ground or self.can_air_dash):
                if not self.on_ground:
                    self.can_air_dash = False
                self.dash_timer = max(1, int(DASH_TIME * 60))
                self.dash_cd = int(DASH_COOLDOWN * 60)
                self.dash_dir = axis if axis else self.facing
                self.facing = self.dash_dir
                self.vy = 0.0
                self.squash = 0.9
                game.audio.play("dash")
                game.add_shake(2.5)
                game.particles.stars(
                    self.rect.centerx, self.rect.centery,
                    fx.mix(body_color, (255, 255, 255), 0.4),
                    count=9, speed=(1.5, 4.5), life=(14, 26), size=(2, 4))

        # горизонталь
        if self.dash_timer > 0:
            self.vx = self.dash_dir * DASH_SPEED * (1.15 if cheats["speed"] else 1.0)
        else:
            if axis:
                accel = (ACCEL if self.on_ground else AIR_ACCEL) * speed_mult
                self.vx += axis * accel
                self.vx = fx.clamp(self.vx, -MAX_SPEED * speed_mult, MAX_SPEED * speed_mult)
                self.facing = axis
            else:
                self.vx *= FRICTION if self.on_ground else 0.965
                if abs(self.vx) < 0.06:
                    self.vx = 0.0

        # прыжки
        if self.jump_buffer > 0:
            max_jumps = 99 if cheats["inf_jump"] else 2
            if self.on_ground or self.coyote > 0:
                self.vy = JUMP_VEL
                self.jumps = 1
                self.on_ground = False
                self.standing_on = None
                self.coyote = 0
                self.jump_buffer = 0
                self.squash = 1.16
                game.audio.play("jump")
                game.particles.dust(self.rect.centerx, self.rect.bottom,
                                    accent, direction=0, count=7)
            elif self.jumps < max_jumps:
                self.vy = DOUBLE_JUMP_VEL
                self.jumps += 1
                self.jump_buffer = 0
                self.squash = 1.18
                game.audio.play("double")
                game.particles.stars(
                    self.rect.centerx, self.rect.centery,
                    fx.mix(accent, (255, 255, 255), 0.35),
                    count=10, speed=(1.0, 4.0), life=(16, 30), size=(2, 4))

        # короткий прыжок
        if not jump_held and self.vy < -5.0:
            self.vy += 0.62

        # гравитация
        if self.dash_timer <= 0:
            gravity = GRAVITY * (0.45 if cheats["moon"] else 1.0)
            self.vy = min(self.vy + gravity, MAX_FALL)

        # --- движение по X ---
        self.x += self.vx
        self.rect.x = round(self.x)
        for platform in level.solids:
            if self.rect.colliderect(platform.rect):
                if self.vx > 0:
                    self.rect.right = platform.rect.left
                elif self.vx < 0:
                    self.rect.left = platform.rect.right
                else:
                    continue
                self.x = float(self.rect.x)
                self.vx = 0.0
                if self.dash_timer > 0:
                    self.dash_timer = 0

        # --- движение по Y ---
        prev_bottom = self.rect.bottom
        was_ground = self.on_ground
        self.y += self.vy
        self.rect.y = round(self.y)
        self.on_ground = False
        self.standing_on = None

        for platform in level.solids:
            if self.rect.colliderect(platform.rect):
                if self.vy > 0:
                    impact = self.vy
                    self.rect.bottom = platform.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    self._land(game, platform, was_ground, impact)
                elif self.vy < 0:
                    self.rect.top = platform.rect.bottom
                    self.y = float(self.rect.y)
                    self.vy = 0.0

        for platform in level.oneways:
            if self.vy >= 0 and self.rect.colliderect(platform.rect):
                if prev_bottom <= platform.rect.top + 2 and self.rect.bottom >= platform.rect.top:
                    impact = self.vy
                    self.rect.bottom = platform.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    self._land(game, platform, was_ground, impact)

        if not self.on_ground:
            self.coyote = max(0.0, self.coyote - 1.0)
        else:
            self.coyote = COYOTE_TIME * 60

        # мягкая посадка
        self.squash += (1.0 - self.squash) * 0.16

        # след рывка
        if self.dash_timer > 0:
            game.particles.add(fx.Particle(
                self.rect.centerx, self.rect.centery,
                -self.facing * 0.6, 0.2, 14,
                fx.mix(accent, (255, 255, 255), 0.25), 5, kind="dot"))

        # падение в бездну
        if self.rect.top > level.height + 160:
            game.kill_player("fall")

    def _land(self, game, platform, was_ground, impact):
        self.on_ground = True
        self.standing_on = platform
        self.jumps = 0
        self.can_air_dash = True
        self.coyote = COYOTE_TIME * 60
        if not was_ground and impact > 7.5:
            self.squash = 0.78
            game.audio.play("land")
            game.add_shake(min(5.0, impact * 0.28))
            palette = PALETTES[game.save.equipped("skin")]
            game.particles.dust(self.rect.centerx, self.rect.bottom,
                                palette["accent"], direction=0, count=9)

    # --- отрисовка -------------------------------------------------------
    def draw(self, surface, offset, save, t):
        if self.dead:
            return
        ox, oy = offset
        cx = self.rect.centerx - ox
        cy = self.rect.centery - oy
        palette = PALETTES[save.equipped("skin")]
        if self.on_ground:
            shadow = fx.soft_ellipse(int(PLAYER_W * 1.35), 11, (82, 56, 38), 80)
            surface.blit(shadow, (cx - shadow.get_width() // 2,
                                  self.rect.bottom - oy - 5))
        alpha = 255
        if self.invuln > 0:
            alpha = 80 if (self.invuln // 4) % 2 else 255
        draw_character(
            surface, (cx, cy), (PLAYER_W, PLAYER_H), palette,
            hat=save.equipped("hat"), eyes=save.equipped("eyes"),
            facing=self.facing, t=t, squash=self.squash, alpha=alpha,
            walk=self.walk_phase if self.on_ground else 0.0,
        )
