"""Constants, palettes and settings for PIXELRUSH."""
from pathlib import Path

# --- screen ---------------------------------------------------------------
WIDTH, HEIGHT = 1280, 720
FPS = 60
FIXED_DT = 1.0 / FPS
TITLE = "PIXELRUSH"

BASE_DIR = Path(__file__).resolve().parent
SAVE_FILE = BASE_DIR / "save.json"

FONT_REGULAR_PATH = Path("/usr/share/fonts/TTF/DejaVuSans.ttf")
FONT_BOLD_PATH = Path("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf")
FONT_REGULAR = str(FONT_REGULAR_PATH) if FONT_REGULAR_PATH.exists() else None
FONT_BOLD = str(FONT_BOLD_PATH) if FONT_BOLD_PATH.exists() else None

# --- player physics (pixels per frame at 60 FPS) --------------------------
GRAVITY = 0.86
MAX_FALL = 19.0
ACCEL = 1.15
AIR_ACCEL = 0.85
MAX_SPEED = 6.4
FRICTION = 0.80
JUMP_VEL = -15.6
DOUBLE_JUMP_VEL = -13.6
COYOTE_TIME = 0.10
JUMP_BUFFER = 0.12
DASH_SPEED = 15.5
DASH_TIME = 0.16
DASH_COOLDOWN = 0.80

PLAYER_W, PLAYER_H = 34, 44

# --- colours --------------------------------------------------------------
WHITE = (255, 252, 245)
INK = (62, 48, 40)
SOFT = (122, 100, 84)
MUTED = (158, 132, 112)
DARK = (48, 38, 32)
PANEL = (255, 248, 236)
PANEL_LIGHT = (255, 253, 247)
CREAM = (255, 246, 231)
SHADOW = (88, 64, 48)

# Kept as named accent slots so modules can share a consistent palette.
NEON_CYAN = (72, 145, 146)     # teal
NEON_PINK = (214, 92, 88)      # coral
NEON_GREEN = (100, 156, 92)    # sage
NEON_GOLD = (222, 158, 56)     # mustard
NEON_PURPLE = (148, 114, 164)  # plum
NEON_RED = (192, 72, 68)       # brick
CHEAT_ACCENT = (214, 92, 88)

# --- customization --------------------------------------------------------
PALETTES = [
    {"name": "Coral",     "body": (238, 111, 94),  "accent": (255, 179, 102), "price": 0},
    {"name": "Mint",      "body": (126, 214, 174), "accent": (64, 124, 118),  "price": 0},
    {"name": "Sky",       "body": (114, 180, 220), "accent": (63, 109, 140),  "price": 30},
    {"name": "Sunflower", "body": (245, 194, 78),  "accent": (196, 120, 52),  "price": 50},
    {"name": "Lavender",  "body": (178, 151, 214), "accent": (118, 86, 148),  "price": 70},
    {"name": "Rose",      "body": (231, 124, 150), "accent": (168, 66, 96),   "price": 120},
    {"name": "Sand",      "body": (226, 198, 156), "accent": (158, 112, 76),  "price": 150},
    {"name": "Cocoa",     "body": (146, 102, 78),  "accent": (244, 196, 118), "price": 250},
    {"name": "Ocean",     "body": (86, 148, 180),  "accent": (224, 156, 84),  "price": 180},
]

HATS = [
    {"name": "No Hat",     "price": 0},
    {"name": "Cap",        "price": 40},
    {"name": "Headphones", "price": 90},
    {"name": "Horns",      "price": 130},
    {"name": "Crown",      "price": 200},
    {"name": "Party Hat",  "price": 260},
    {"name": "Halo",       "price": 350},
    {"name": "Beret",      "price": 170},
    {"name": "Flower",     "price": 230},
]

EYES = [
    {"name": "Classic", "price": 0},
    {"name": "Happy",   "price": 0},
    {"name": "Angry",   "price": 50},
    {"name": "Cool",    "price": 90},
    {"name": "Stars",   "price": 160},
    {"name": "Wink",    "price": 110},
    {"name": "Sleepy",  "price": 70},
]

CATEGORIES = [
    {"key": "skins", "equip": "skin", "label": "BODY COLOR", "items": PALETTES},
    {"key": "hats",  "equip": "hat",  "label": "HAT",        "items": HATS},
    {"key": "eyes",  "equip": "eyes", "label": "EYES",       "items": EYES},
]

DEFAULT_SETTINGS = {
    "fullscreen": False,
    "screen_shake": True,
    "particles": False,
    "show_fps": False,
}

DEFAULT_SAVE = {
    "coins": 0,
    "unlocked": {"skins": [0, 1], "hats": [0], "eyes": [0, 1]},
    "equipped": {"skin": 0, "hat": 0, "eyes": 0},
    "best": {},
    "muted": False,
    "settings": dict(DEFAULT_SETTINGS),
}

# --- controls -------------------------------------------------------------
MOVE_LEFT = ("a", "left")
MOVE_RIGHT = ("d", "right")
JUMP_KEYS = ("space", "w", "up")
DASH_KEYS = ("lshift", "rshift")
