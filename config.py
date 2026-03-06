"""
Конфигурация бота "Мастер документов"
Здесь хранятся все настройки и переменные окружения
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Токен бота (получить у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ID администратора (куда отправлять копии документов)
# Узнать свой ID можно у бота @userinfobot
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Путь к базе данных
DATABASE_PATH = "documents.db"

# Папка для временных файлов PDF
TEMP_DIR = "temp"

# Название бота
BOT_NAME = "Мастер документов"

# Валюта по умолчанию
CURRENCY = "₽"

# Ставка НДС (по умолчанию без НДС)
VAT_RATE = 0  # 0 - без НДС, 20 - 20%
