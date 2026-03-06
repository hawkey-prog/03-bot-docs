"""
Обработчик команд /start и /help
Главное меню бота с кнопками
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import add_user, get_user_documents

router = Router()


# Главное меню с кнопками
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создаёт главное меню с кнопками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🧾 Создать счёт"),
                KeyboardButton(text="📄 Создать акт")
            ],
            [
                KeyboardButton(text="📁 Мои документы"),
                KeyboardButton(text="📞 Помощь")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


# Команда /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start - приветствие"""
    
    # Добавляем пользователя в базу
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    
    await message.answer(
        f"👋 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
        f"Я — <b>Мастер документов</b>, бот для создания счетов и актов.\n\n"
        f"📝 <b>Что я умею:</b>\n"
        f"• Создавать счета на оплату\n"
        f"• Создавать акты выполненных работ\n"
        f"• Сохранять историю документов\n"
        f"• Отправлять готовые PDF-файлы\n\n"
        f"Выберите действие в меню ниже 👇",
        reply_markup=get_main_keyboard()
    )


# Команда /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help - справка"""
    
    await message.answer(
        "📖 <b>Справка по боту</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Запустить бота\n"
        "/help - Показать эту справку\n"
        "/mydocs - Мои документы\n\n"
        "<b>Как создать документ:</b>\n"
        "1. Нажмите '🧾 Создать счёт' или '📄 Создать акт'\n"
        "2. Следуйте инструкциям бота\n"
        "3. Подтвердите данные\n"
        "4. Получите готовый PDF-файл\n\n"
        "<b>Важно:</b>\n"
        "• Все документы сохраняются в истории\n"
        "• Копия отправляется администратору\n"
        "• PDF можно скачать и распечатать\n\n"
        "📞 <b>Поддержка:</b> @support_bot"
    )


# Обработка кнопки "Помощь"
@router.message(F.text == "📞 Помощь")
async def btn_help(message: Message):
    """Обработчик кнопки Помощь"""
    await cmd_help(message)


# Обработка кнопки "Мои документы"
@router.message(F.text == "📁 Мои документы")
async def btn_mydocs(message: Message):
    """Обработчик кнопки Мои документы"""
    await show_my_documents(message)


async def show_my_documents(message: Message):
    """Показывает список документов пользователя"""
    
    documents = await get_user_documents(message.from_user.id)
    
    if not documents:
        await message.answer(
            "📁 <b>У вас пока нет документов</b>\n\n"
            "Создайте свой первый документ, выбрав соответствующую кнопку в меню."
        )
        return
    
    # Формируем список последних 10 документов
    text = "📁 <b>Ваши документы</b> (последние 10):\n\n"
    
    for doc in documents[-10:]:
        doc_type = "🧾 Счёт" if doc["doc_type"] == "invoice" else "📄 Акт"
        date = doc["created_at"][:10]
        text += f"{doc_type} №{doc['number']} от {date}\n"
        text += f"   Сумма: {doc['amount']} ₽\n\n"
    
    text += f"Всего документов: {len(documents)}"
    
    await message.answer(text)
