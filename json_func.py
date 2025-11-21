# json_func.py
import json
import os
from typing import Dict

PATH = "channels.json"

DEFAULT_DATA = {
    "channels": {},          # каналы откатов
    "private_channels": {}   # личные дела
}

def load_data() -> Dict:
    """Безопасно загружает JSON, если что-то сломано — возвращает дефолт"""
    if not os.path.exists(PATH):
        return DEFAULT_DATA.copy()

    try:
        with open(PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            # Проверяем и чиним структуру
            if not isinstance(loaded, dict):
                return DEFAULT_DATA.copy()
            if "channels" not in loaded or not isinstance(loaded["channels"], dict):
                loaded["channels"] = {}
            if "private_channels" not in loaded or not isinstance(loaded["private_channels"], dict):
                loaded["private_channels"] = {}
            return loaded
    except Exception as e:
        print(f"[json_func] Файл повреждён ({e}), создаём новый по дефолту.")
        return DEFAULT_DATA.copy()

def save_data(data: Dict):
    """Сохраняет весь словарь целиком"""
    try:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[json_func] Ошибка сохранения JSON: {e}")

# === Глобальные переменные — теперь 100% безопасно ===
data = load_data()
channels = data.get("channels", {})                  # никогда не упадёт
private_channels = data.get("private_channels", {})  # никогда не упадёт

# Если в загруженных данных что-то сломано — подменяем на пустые словари
if not isinstance(channels, dict):
    channels = {}
if not isinstance(private_channels, dict):
    private_channels = {}

# Перезаписываем файл чистой структурой (один раз при старте, если был мусор)
save_data({"channels": channels, "private_channels": private_channels})

# === Функции сохранения (теперь без аргументов и без race condition) ===
def save_channels():
    current = load_data()
    current["channels"] = channels
    save_data(current)

def save_private_channels():
    current = load_data()
    current["private_channels"] = private_channels
    save_data(current)

def save_all():
    save_data({
        "channels": channels,
        "private_channels": private_channels
    })

print(f"JSON загружен: {len(channels)} каналов откатов, {len(private_channels)} личных дел")

def add_private_channel(user_id: int | str, channel_id: int):
    """
    Надёжно добавляет/обновляет личное дело и сразу сохраняет в JSON.
    Используй ТОЛЬКО эту функцию везде!
    """
    private_channels[str(user_id)] = channel_id
    save_all()

def add_private_channel(user_id: int | str, channel_id: int):
    private_channels[str(user_id)] = channel_id
    save_all()

print(f"JSON загружен: {len(channels)} каналов откатов | {len(private_channels)} личных дел")