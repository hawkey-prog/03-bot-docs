"""
Обработчик команды /mydocs - просмотр списка документов
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_user_documents, get_document_by_id

router = Router()


# Команда /mydocs
@router.message(Command("mydocs"))
async def cmd_mydocs(message: Message):
    """Показывает список документов пользователя"""
    
    await show_documents_list(message, page=0)


async def show_documents_list(message: Message, page: int = 0):
    """Показывает список документов с пагинацией"""
    
    documents = await get_user_documents(message.from_user.id)
    
    if not documents:
        await message.answer(
            "📁 <b>У вас пока нет документов</b>\n\n"
            "Создайте свой первый документ, выбрав:\n"
            "🧾 Создать счёт\n"
            "📄 Создать акт"
        )
        return
    
    # Пагинация: по 10 документов на странице
    per_page = 10
    total_pages = (len(documents) + per_page - 1) // per_page
    
    if page >= total_pages:
        page = total_pages - 1
    if page < 0:
        page = 0
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(documents))
    
    # Формируем текст для текущей страницы
    text = f"📁 <b>Ваши документы</b> (стр. {page + 1}/{total_pages}):\n\n"
    
    for i, doc in enumerate(documents[start_idx:end_idx], start=start_idx + 1):
        doc_type = "🧾" if doc["doc_type"] == "invoice" else "📄"
        date = doc["created_at"][:10]
        text += f"{i}. {doc_type} №{doc['number']} от {date}\n"
        text += f"   💰 {doc['amount']} ₽\n\n"
    
    # Кнопки навигации
    keyboard_buttons = []
    
    # Кнопки для каждого документа на странице
    for doc in documents[start_idx:end_idx]:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📄 №{doc['number']}",
                callback_data=f"doc_view_{doc['id']}"
            )
        ])
    
    # Кнопки навигации по страницам
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"docs_page_{page - 1}")
        )
    
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"docs_page_{page + 1}")
        )
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=keyboard)


# Просмотр конкретного документа
@router.callback_query(F.data.startswith("doc_view_"))
async def view_document(callback: CallbackQuery):
    """Показывает детали документа"""
    
    doc_id = int(callback.data.split("_")[-1])
    document = await get_document_by_id(doc_id, callback.from_user.id)
    
    if not document:
        await callback.answer("Документ не найден", show_alert=True)
        return
    
    doc_type = "🧾 Счёт" if document["doc_type"] == "invoice" else "📄 Акт"
    
    text = f"<b>{doc_type}</b>\n\n"
    text += f"🔢 Номер: {document['number']}\n"
    text += f"📅 Дата: {document['date']}\n"
    text += f"💰 Сумма: {document['amount']} ₽\n"
    text += f"📦 Описание: {document['description']}\n"
    text += f"🏢 " + ("Плательщик" if document["doc_type"] == "invoice" else "Заказчик") + f": {document['payer']}\n"
    text += f"📅 Создан: {document['created_at']}\n"
    
    # Кнопка для скачивания
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Скачать PDF", callback_data=f"doc_download_{doc_id}")],
            [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="docs_back")]
        ]
    )
    
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


# Скачивание документа
@router.callback_query(F.data.startswith("doc_download_"))
async def download_document(callback: CallbackQuery):
    """Отправляет файл документа"""
    
    doc_id = int(callback.data.split("_")[-1])
    document = await get_document_by_id(doc_id, callback.from_user.id)
    
    if not document or not document["file_path"]:
        await callback.answer("Файл не найден", show_alert=True)
        return
    
    try:
        with open(document["file_path"], "rb") as f:
            doc_type = "Счёт" if document["doc_type"] == "invoice" else "Акт"
            await callback.message.answer_document(
                document=f,
                caption=f"{doc_type} №{document['number']} от {document['date']}"
            )
        await callback.answer("Файл отправлен")
    except FileNotFoundError:
        await callback.answer("Файл не найден на сервере", show_alert=True)


# Возврат к списку
@router.callback_query(F.data == "docs_back")
async def docs_back(callback: CallbackQuery):
    """Возврат к списку документов"""
    
    await callback.message.delete()
    await show_documents_list(callback.message)
    await callback.answer()


# Пагинация
@router.callback_query(F.data.startswith("docs_page_"))
async def docs_page(callback: CallbackQuery):
    """Переключение страницы списка документов"""
    
    page = int(callback.data.split("_")[-1])
    
    await callback.message.delete()
    await show_documents_list(callback.message, page=page)
    await callback.answer()
