# settings.py
import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 0],  # Зеленый по умолчанию
    "grid_overlay": True,
    "sound": True,
    "username": ""
}


def load_settings():
    """Загружает настройки из файла или возвращает дефолтные"""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Дополняем недостающие ключи
        for key, value in DEFAULT_SETTINGS.items():
            if key not in data:
                data[key] = value
        return data
    except:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Сохраняет настройки в файл"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False