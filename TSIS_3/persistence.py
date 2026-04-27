import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# ====================== LEADERBOARD ======================

def load_leaderboard():
    """Загружает таблицу лидеров из файла. Возвращает список словарей."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_leaderboard(entries):
    """Сохраняет список лидеров (макс. 10 записей, сортировка по score DESC)."""
    entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def add_entry(name: str, score: int, distance: int):
    """Добавляет/обновляет запись. Для каждого имени сохраняется только лучший score."""
    entries = load_leaderboard()

    # Ищем существующую запись
    for entry in entries:
        if entry["name"].lower() == name.lower():
            if score > entry["score"]:
                entry["score"] = score
                entry["distance"] = distance
            return save_leaderboard(entries)

    # Если имени нет — добавляем новую
    entries.append({"name": name, "score": score, "distance": distance})
    save_leaderboard(entries)
    return load_leaderboard()


# ====================== SETTINGS ======================

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   [0, 100, 255],   # RGB
    "difficulty":  "normal",        # easy / normal / hard
    "username":    ""
}


def load_settings():
    """Загружает настройки. Недостающие ключи берутся из DEFAULT_SETTINGS."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Дополняем дефолтами на случай неполного файла
        for k, v in DEFAULT_SETTINGS.items():
            if k not in data:
                data[k] = v
        return data
    except (json.JSONDecodeError, IOError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Сохраняет настройки в файл."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
