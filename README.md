# PIXELRUSH

A bright, colorful platformer made with Python and pygame-ce: three handmade levels,
spikes, coins, moving platforms, a double jump, a dash and a wardrobe full of
cosmetic items. No neon, no image assets — the whole world is drawn in code.

![PIXELRUSH preview](preview.png)

## What's inside

- **3 levels** with distinct natural themes: sunny meadow, teal coast and warm canyon.
- **Spikes, coins, checkpoints and a finish arch.** Each level now has a tighter set of 19–24 coins.
- **Moving platforms**: horizontal lifts and vertical elevators that carry the player.
- **Double jump and dash** for fast, expressive movement.
- **A simple head-and-limbs hero** with a clean face, plus **cosmetics**: 9 body colors,
  9 hats and 7 eye styles. Some items are free, the rest are unlocked with coins.
- **Settings** for fullscreen, sound, screen shake, particles and an FPS counter.
- **Save data** in `save.json`: coins, purchases, the current outfit, best runs and settings.
- **A small cheat menu** on `\` with toggles and one-shot actions.
- **Procedural audio and chiptune music** — no external sound files.
- **No image assets**: the character, platforms, backgrounds and effects are all
  drawn with code.

## Requirements

- Python 3.10+
- pygame-ce

## Install

```bash
cd pixelrush

# option 1: virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# option 2: system Python
python3 -m pip install -r requirements.txt
```

If regular `pygame` is already installed, remove it before installing `pygame-ce`:

```bash
python3 -m pip uninstall pygame
python3 -m pip install pygame-ce
```

## Run

```bash
cd /home/koulbi/python/neon_dash
python3 main.py
```

Or use the helper script:

```bash
./run.sh
```

## Controls

| Keys | Action |
| --- | --- |
| `A` / `D` or `←` / `→` | run |
| `Space` / `W` / `↑` | jump; press again in mid-air for a double jump |
| `Shift` | dash |
| `R` | restart the level |
| `Esc` | pause / go back |
| `\` | open or close the cheat menu |
| `M` | toggle sound |
| `Enter` | confirm a selection |

The menu and wardrobe also support the mouse: hover and click cards or buttons.
Settings are available from both the main menu and the pause menu.
In the wardrobe, `↑`/`↓` switch category, `←`/`→` pick an item and `Enter`
equips or buys it. During a level the HUD stays clean: it shows only the level,
time, coins, deaths and the dash cooldown. No control hints are shown while playing.

## Gameplay

- Collect **coins** — they go straight into your wallet. Coin layouts are deliberately
  sparse: 24 coins in the meadow, 23 on the coast and 19 in the canyon.
- **Spikes** are deadly. After a death the player returns to the last checkpoint.
- **Double jump** and **dash** help you clear wide gaps.
- **Moving platforms** travel between two points and carry the player standing
  on them. Vertical lifts are worth waiting for.
- Each level awards 1–3 stars based on the share of collected coins.
- Best results (time and coins) are saved for every level.

## Wardrobe and coins

Coins are spent on cosmetics in the **Wardrobe**. The starting set includes two
body colors, two eye styles and no hat; everything else is bought with coins.
Prices are shown on the cards. If you don't have enough coins, the status bar
tells you so. Purchased items and the current outfit are saved automatically.

## Settings

Open **SETTINGS** from the main menu or the pause menu. Changes are saved
immediately.

- **Fullscreen** — switches the game to fullscreen. The game keeps a logical
  1280×720 canvas and scales it to your desktop, so the layout stays consistent.
- **Sound** — music and sound effects on/off (the `M` key does the same).
- **Screen Shake** — camera impact when you die or land hard.
- **Particles** — sparkles, dust and confetti. Off by default for a cleaner,
  calmer look; turn it back on if you want the extra effects.
- **Show FPS** — a small frame-rate counter under the time panel during play.

If fullscreen cannot be created, the game falls back to a regular window and
remembers that choice.

## Cheat menu

Press `\` in any state. It is small but useful:

- **God Mode** — spikes and falls no longer hurt.
- **Infinite Jump** — as many mid-air jumps as you like.
- **Turbo Speed ×1.8** — faster running and dashing.
- **Moon Gravity** — higher jumps and a slower fall.
- **Coin Magnet** — coins fly straight to the player.
- **Noclip** — free flight with `WASD` or the arrow keys.
- **Slow-Mo ×0.5** — slows down game time.
- **+250 Coins** — top up your wallet.
- **Unlock Everything** — unlock every cosmetic item.
- **Skip Level** — jump to the next level (only while playing).

Toggle cheats last until you close the game and are not written to disk. Coin
and cosmetic actions are saved immediately.

## Save data

`save.json` is created next to the game (`neon_dash/save.json`) after the first
purchase, finished level or clean exit. Delete it to start fresh: 0 coins,
starter cosmetics and empty records.

Corrupted JSON is handled gracefully — the game falls back to default values.

## Project layout

```
neon_dash/
├── main.py          # entry point and game loop
├── game.py          # states, cheats, events, progress
├── level.py         # levels, platforms, spikes, coins, finish
├── player.py        # physics, jump, dash, character art
├── ui.py            # menu, settings, wardrobe, HUD, pause, cheat menu
├── fx.py            # optional particles, camera, gradients, panels
├── audio.py         # procedural SFX and chiptune music
├── save.py          # save.json reading and writing
├── config.py        # constants, palettes, prices, fonts
├── preview.png      # README screenshot
├── requirements.txt
└── run.sh
```

## Notes

- The game targets a 1280×720 window at 60 FPS. Fullscreen keeps that logical
  resolution and scales it to the display.
- Audio is synthesized at startup; if no audio device is available, the game
  keeps running silently.
- Fonts come from system DejaVu Sans; if missing, pygame's built-in font is used.
- Every level is beatable without cheats. Some moving platforms are easier to
  wait for than to jump past.
- Particles are off by default, but the rest of the game still uses the camera and
  toast messages for feedback.
