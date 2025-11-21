from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен из .env
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ Не найден TOKEN в .env. Проверь, что .env существует и содержит токен.")
