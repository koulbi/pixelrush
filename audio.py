"""Procedural sound effects and chiptune music — no external files."""
import array
import math
import random

import pygame

SR = 44100


def _osc(wave, phase, rng):
    if wave == "sine":
        return math.sin(phase)
    if wave == "square":
        return 1.0 if math.sin(phase) >= 0 else -1.0
    if wave == "saw":
        return 2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0
    if wave == "triangle":
        return 2.0 * abs(2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0) - 1.0
    if wave == "noise":
        return rng.uniform(-1.0, 1.0)
    return 0.0


def _to_sound(samples, volume=1.0):
    buf = array.array("h")
    peak = max(1e-6, max(abs(s) for s in samples) if samples else 1.0)
    norm = min(1.0, 1.0 / peak)
    for s in samples:
        value = int(max(-1.0, min(1.0, s * norm * volume)) * 32000)
        buf.append(value)
        buf.append(value)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _render(events, duration, volume=0.5, fade_out=0.0):
    """events: (start, f0, f1, dur, wave, vol, decay)."""
    total = int(duration * SR)
    buf = [0.0] * total
    rng = random.Random(7)
    for start, f0, f1, dur, wave, vol, decay in events:
        begin = int(start * SR)
        count = int(dur * SR)
        phase = 0.0
        filtered = 0.0
        for i in range(count):
            idx = begin + i
            if idx >= total:
                break
            t = i / count
            freq = f0 + (f1 - f0) * t
            phase += 2.0 * math.pi * freq / SR
            raw = _osc(wave, phase, rng)
            if wave == "noise":
                filtered = filtered * 0.55 + raw * 0.45
                raw = filtered
            attack = min(1.0, i / max(1.0, 0.004 * SR))
            env = attack * math.exp(-decay * t)
            buf[idx] += raw * env * vol
    if fade_out > 0:
        n = min(total, int(fade_out * SR))
        for i in range(n):
            buf[total - n + i] *= i / n
    return _to_sound(buf, volume)


class Audio:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        self.music = None
        self.music_channel = None
        try:
            pygame.mixer.pre_init(SR, -16, 2, 512)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            self.enabled = True
        except pygame.error:
            self.enabled = False
            return
        try:
            self._build_sfx()
            self._build_music()
            self.music_channel = pygame.mixer.Channel(0)
            self.music_channel.play(self.music, loops=-1)
            self.music_channel.set_volume(0.5)
        except (pygame.error, MemoryError):
            self.enabled = False

    # --- генерация -------------------------------------------------------
    def _build_sfx(self):
        self.sounds["jump"] = _render(
            [(0.0, 320, 560, 0.13, "square", 0.20, 7.0)], 0.14, 0.5
        )
        self.sounds["double"] = _render(
            [(0.0, 460, 880, 0.14, "triangle", 0.28, 8.0)], 0.15, 0.5
        )
        self.sounds["dash"] = _render(
            [(0.0, 700, 180, 0.20, "noise", 0.30, 9.0)], 0.21, 0.45, fade_out=0.05
        )
        self.sounds["coin"] = _render(
            [
                (0.0, 1108, 1108, 0.07, "sine", 0.35, 10.0),
                (0.055, 1661, 1661, 0.14, "sine", 0.30, 11.0),
            ],
            0.21, 0.45,
        )
        self.sounds["death"] = _render(
            [
                (0.0, 420, 90, 0.32, "saw", 0.28, 5.0),
                (0.02, 210, 60, 0.30, "square", 0.16, 5.0),
            ],
            0.34, 0.5, fade_out=0.08,
        )
        self.sounds["click"] = _render(
            [(0.0, 740, 700, 0.045, "square", 0.22, 16.0)], 0.05, 0.5
        )
        self.sounds["land"] = _render(
            [(0.0, 220, 110, 0.08, "sine", 0.28, 14.0)], 0.09, 0.4
        )
        self.sounds["checkpoint"] = _render(
            [
                (0.0, 660, 660, 0.10, "triangle", 0.26, 8.0),
                (0.08, 990, 990, 0.16, "triangle", 0.24, 8.0),
            ],
            0.26, 0.45,
        )
        self.sounds["buy"] = _render(
            [
                (0.0, 659, 659, 0.09, "triangle", 0.25, 9.0),
                (0.075, 830, 830, 0.09, "triangle", 0.25, 9.0),
                (0.15, 1046, 1046, 0.20, "triangle", 0.28, 7.0),
            ],
            0.4, 0.5,
        )
        self.sounds["error"] = _render(
            [(0.0, 170, 130, 0.13, "square", 0.20, 9.0)], 0.14, 0.4
        )
        self.sounds["win"] = _render(
            [
                (0.0, 523, 523, 0.12, "triangle", 0.24, 7.0),
                (0.10, 659, 659, 0.12, "triangle", 0.24, 7.0),
                (0.20, 784, 784, 0.12, "triangle", 0.24, 7.0),
                (0.30, 1046, 1046, 0.16, "triangle", 0.26, 6.0),
                (0.44, 1318, 1318, 0.30, "triangle", 0.30, 4.0),
            ],
            0.8, 0.5,
        )

    def _build_music(self):
        step = 0.16
        bars = 4
        steps = bars * 8
        total = steps * step
        buf = [0.0] * int(total * SR)
        rng = random.Random(11)

        chords = [
            [220.00, 261.63, 329.63],   # Am
            [174.61, 220.00, 261.63],   # F
            [261.63, 329.63, 392.00],   # C
            [196.00, 246.94, 293.66],   # G
        ]
        roots = [110.0, 87.31, 130.81, 98.0]

        def add(start, freq, dur, wave, vol, decay, slide=1.0):
            begin = int(start * SR)
            count = int(dur * SR)
            phase = 0.0
            filtered = 0.0
            for i in range(count):
                idx = begin + i
                if idx >= len(buf):
                    break
                t = i / count
                f = freq * (1.0 + (slide - 1.0) * t)
                phase += 2.0 * math.pi * f / SR
                raw = _osc(wave, phase, rng)
                if wave == "noise":
                    filtered = filtered * 0.4 + raw * 0.6
                    raw = filtered
                attack = min(1.0, i / max(1.0, 0.003 * SR))
                env = attack * math.exp(-decay * t)
                buf[idx] += raw * env * vol

        for bar in range(bars):
            t0 = bar * 8 * step
            add(t0, roots[bar], 8 * step * 0.92, "triangle", 0.10, 0.9)
            add(t0, roots[bar] * 2, 8 * step * 0.9, "sine", 0.05, 0.9)
            for k in range(8):
                note = chords[bar][k % 3] * (2.0 if k % 4 >= 2 else 1.0)
                add(t0 + k * step, note, step * 0.85, "square", 0.028, 5.5)
            for k in (0, 4):
                add(t0 + k * step, 150, 0.16, "sine", 0.20, 18.0, slide=0.32)
            for k in (2, 6):
                add(t0 + k * step, 100, 0.10, "sine", 0.10, 22.0, slide=0.5)
            for k in range(1, 8, 2):
                add(t0 + k * step, 6000, 0.035, "noise", 0.045, 38.0)

        # мягкое затухание на стыке петли
        fade = int(0.06 * SR)
        for i in range(fade):
            buf[len(buf) - fade + i] *= i / fade
        self.music = _to_sound(buf, 0.55)

    # --- API -------------------------------------------------------------
    def play(self, name):
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def set_muted(self, muted):
        if not self.enabled:
            self.muted = muted
            return
        self.muted = bool(muted)
        if self.muted:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()
            if self.music_channel is not None and not self.music_channel.get_busy():
                self.music_channel.play(self.music, loops=-1)

    def toggle_mute(self):
        self.set_muted(not self.muted)
        return self.muted
