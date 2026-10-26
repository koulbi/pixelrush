"""Save data: coins, unlocked cosmetics and best runs."""
import copy
import json

from config import CATEGORIES, DEFAULT_SAVE, DEFAULT_SETTINGS, SAVE_FILE


class Save:
    def __init__(self):
        self.data = copy.deepcopy(DEFAULT_SAVE)
        self.load()

    # --- диск ------------------------------------------------------------
    def load(self):
        try:
            raw = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(raw, dict):
            return
        self._merge(self.data, raw)
        self._sanitize()

    def _merge(self, base, extra):
        for key, value in extra.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge(base[key], value)
            else:
                base[key] = value

    def _sanitize(self):
        d = self.data
        try:
            d["coins"] = max(0, int(d.get("coins", 0)))
        except (TypeError, ValueError):
            d["coins"] = 0
        if not isinstance(d.get("unlocked"), dict):
            d["unlocked"] = copy.deepcopy(DEFAULT_SAVE["unlocked"])
        if not isinstance(d.get("equipped"), dict):
            d["equipped"] = copy.deepcopy(DEFAULT_SAVE["equipped"])
        for cat in CATEGORIES:
            key, count = cat["key"], len(cat["items"])
            raw = d["unlocked"].get(key, [])
            if not isinstance(raw, list):
                raw = []
            unlocked = [i for i in raw if isinstance(i, int) and 0 <= i < count]
            if 0 not in unlocked:
                unlocked.insert(0, 0)
            d["unlocked"][key] = sorted(set(unlocked))
            eq = d["equipped"].get(cat["equip"], 0)
            if eq not in d["unlocked"][key]:
                eq = unlocked[0]
            d["equipped"][cat["equip"]] = eq
        if not isinstance(d.get("best"), dict):
            d["best"] = {}
        d["muted"] = bool(d.get("muted", False))
        if not isinstance(d.get("settings"), dict):
            d["settings"] = {}
        for key, default in DEFAULT_SETTINGS.items():
            d["settings"][key] = bool(d["settings"].get(key, default))

    def write(self):
        try:
            SAVE_FILE.write_text(
                json.dumps(self.data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    # --- монеты ----------------------------------------------------------
    @property
    def coins(self):
        return self.data["coins"]

    def add_coins(self, amount):
        self.data["coins"] = max(0, self.data["coins"] + int(amount))

    # --- скины -----------------------------------------------------------
    def is_unlocked(self, key, index):
        return index in self.data["unlocked"][key]

    def unlock(self, key, index):
        if index not in self.data["unlocked"][key]:
            self.data["unlocked"][key].append(index)
            self.data["unlocked"][key].sort()

    def equip(self, equip_key, index):
        self.data["equipped"][equip_key] = index

    def equipped(self, equip_key):
        return self.data["equipped"][equip_key]

    def guessed(self, category):
        return self.data["equipped"][category["equip"]]

    # --- settings --------------------------------------------------------
    def setting(self, key):
        return bool(self.data["settings"].get(key, DEFAULT_SETTINGS.get(key, False)))

    def set_setting(self, key, value):
        self.data["settings"][key] = bool(value)

    # --- рекорды ---------------------------------------------------------
    def record(self, level_index):
        return self.data["best"].get(str(level_index))

    def update_record(self, level_index, time_spent, coins, deaths, total_coins):
        old = self.record(level_index)
        entry = {
            "time": round(time_spent, 2),
            "coins": coins,
            "total": total_coins,
            "deaths": deaths,
        }
        if old is None:
            changed = True
        else:
            changed = (
                coins > old.get("coins", 0)
                or (coins == old.get("coins", 0) and time_spent < old.get("time", 10**9))
            )
        if changed:
            self.data["best"][str(level_index)] = entry
        return changed
