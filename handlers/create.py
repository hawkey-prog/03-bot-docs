"""
Обработчик создания документов (счета и акты)
Использует машину состояний (FSM) для пошагового диалога
"""

from aiogram import Router, F, FormDispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import add_document, get_user_documents
from services.pdf_generator import generate_invoice_pdf, generate_act_pdf
from config import ADMIN_ID

router = Router()


# Машина состояний для создания документа
class DocumentForm(StatesGroup):
    """Состояния формы создания документа"""
    type_choice = State()      # Выбор типа документа
    number = State()           # Номер документа
    date = State()             # Дата документа
    description = State()      # Описание товара/услуги
    amount = State()           # Сумма
    payer = State()            # Плательщик/Заказчик
    confirm = State()          # Подтверждение


# Хранилище данных формы
form_data = {}


# Обработка кнопок создания
@router.message(F.text.in_(["🧾 Создать счёт", "📄 Создать акт"]))
async def start_create(message: Message, state: FSMContext):
    """Начало процесса создания документа"""
    
    doc_type = "invoice" if "счёт" in message.text else "act"
    doc_name = "счёт" if doc_type == "invoice" else "акт"
    
    # Инициализация данных формы
    form_data[message.from_user.id] = {
        "type": doc_type,
        "type_name": doc_name
    }
    
    await state.set_state(DocumentForm.number)
    
    await message.answer(
        f"📝 <b>Создание документа: {doc_name.capitalize()}</b>\n\n"
        f"Введите <b>номер документа</b> (например: 1, 2, 15/2024):\n"
        f"<i>или нажмите /cancel для отмены</i>",
        reply_markup=ReplyKeyboardRemove()
    )


# Ввод номера документа
@router.message(DocumentForm.number)
async def process_number(message: Message, state: FSMContext):
    """Обработка номера документа"""
    
    number = message.text.strip()
    
    if len(number) > 20:
        await message.answer("❌ Номер слишком длинный. Введите номер до 20 символов:")
        return
    
    await state.update_data(number=number)
    form_data[message.from_user.id]["number"] = number
    
    await state.set_state(DocumentForm.date)
    
    from datetime import datetime
    today = datetime.now().strftime("%d.%m.%Y")
    
    await message.answer(
        f"📅 Введите <b>дату документа</b> (ДД.ММ.ГГГГ):\n"
        f"<i>или нажмите Enter для даты по умолчанию ({today})</i>"
    )


# Ввод даты документа
@router.message(DocumentForm.date)
async def process_date(message: Message, state: FSMContext):
    """Обработка даты документа"""
    
    from datetime import datetime
    
    date_text = message.text.strip()
    
    if not date_text or date_text.lower() == "enter":
        date_text = datetime.now().strftime("%d.%m.%Y")
    
    # Простая валидация даты
    try:
        datetime.strptime(date_text, "%d.%m.%Y")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ:")
        return
    
    await state.update_data(date=date_text)
    form_data[message.from_user.id]["date"] = date_text
    
    doc_name = form_data[message.from_user.id]["type_name"]
    
    await state.set_state(DocumentForm.description)
    
    if doc_name == "счёт":
        await message.answer(
            "📦 Введите <b>наименование товара/услуги</b>:\n"
            "<i>(например: Консультационные услуги, Товар А)</i>"
        )
    else:
        await message.answer(
            "📦 Введите <b>наименование выполненной работы/услуги</b>:\n"
            "<i>(например: Разработка сайта, Консультация)</i>"
        )


# Ввод описания
@router.message(DocumentForm.description)
async def process_description(message: Message, state: FSMContext):
    """Обработка описания товара/услуги"""
    
    description = message.text.strip()
    
    if len(description) < 3:
        await message.answer("❌ Описание слишком короткое. Введите подробнее:")
        return
    
    await state.update_data(description=description)
    form_data[message.from_user.id]["description"] = description
    
    await state.set_state(DocumentForm.amount)
    
    await message.answer(
        "💰 Введите <b>сумму документа</b> (число, без пробелов):\n"
        "<i>(например: 10000, 50000.50)</i>"
    )


# Ввод суммы
@router.message(DocumentForm.amount)
async def process_amount(message: Message, state: FSMContext):
    """Обработка суммы документа"""
    
    amount_text = message.text.strip().replace(",", ".")
    
    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректную сумму (положительное число):")
        return
    
    await state.update_data(amount=amount)
    form_data[message.from_user.id]["amount"] = amount
    
    doc_name = form_data[message.from_user.id]["type_name"]
    
    await state.set_state(DocumentForm.payer)
    
    if doc_name == "счёт":
        await message.answer(
            "🏢 Введите <b>наименование плательщика</b>:\n"
            "<i>(например: ООО Ромашка, ИП Иванов А.А.)</i>"
        )
    else:
        await message.answer(
            "🏢 Введите <b>наименование заказчика</b>:\n"
            "<i>(например: ООО Ромашка, ИП Иванов А.А.)</i>"
        )


# Ввод плательщика/заказчика
@router.message(DocumentForm.payer)
async def process_payer(message: Message, state: FSMContext):
    """Обработка плательщика/заказчика"""
    
    payer = message.text.strip()
    
    if len(payer) < 3:
        await message.answer("❌ Введите корректное наименование:")
        return
    
    await state.update_data(payer=payer)
    form_data[message.from_user.id]["payer"] = payer
    
    # Получаем все данные для подтверждения
    data = await state.get_data()
    doc_name = form_data[message.from_user.id]["type_name"]
    
    # Формируем текст подтверждения
    confirm_text = f"📋 <b>Проверьте данные документа:</b>\n\n"
    confirm_text += f"📄 Тип: {doc_name.capitalize()}\n"
    confirm_text += f"🔢 Номер: {data['number']}\n"
    confirm_text += f"📅 Дата: {data['date']}\n"
    confirm_text += f"📦 Описание: {data['description']}\n"
    confirm_text += f"💰 Сумма: {data['amount']} ₽\n"
    
    if doc_name == "счёт":
        confirm_text += f"🏢 Плательщик: {data['payer']}\n"
    else:
        confirm_text += f"🏢 Заказчик: {data['payer']}\n"
    
    confirm_text += "\n<b>Всё верно?</b>"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_create")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_create")]
        ]
    )
    
    await state.set_state(DocumentForm.confirm)
    
    await message.answer(confirm_text, reply_markup=keyboard)


# Подтверждение создания
@router.callback_query(F.data == "confirm_create", StateFilter(DocumentForm.confirm))
async def confirm_create(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и создание документа"""
    
    data = await state.get_data()
    user_id = callback.from_user.id
    doc_data = form_data.get(user_id, {})
    
    # Генерация PDF
    try:
        if doc_data["type"] == "invoice":
            pdf_path = await generate_invoice_pdf(data, user_id)
        else:
            pdf_path = await generate_act_pdf(data, user_id)
        
        # Сохранение в БД
        doc_id = await add_document(
            user_id=user_id,
            doc_type=doc_data["type"],
            number=data["number"],
            date=data["date"],
            description=data["description"],
            amount=data["amount"],
            payer=data["payer"],
            file_path=pdf_path
        )
        
        # Отправка файла пользователю
        doc_name = "Счёт" if doc_data["type"] == "invoice" else "Акт"
        
        await callback.message.answer(
            f"✅ <b>Документ создан!</b>\n\n"
            f"{doc_name} №{data['number']} от {data['date']}\n"
            f"Сумма: {data['amount']} ₽\n\n"
            f"Файл отправлен ниже 👇"
        )
        
        with open(pdf_path, "rb") as pdf_file:
            await callback.message.answer_document(
                document=pdf_file,
                caption=f"{doc_name} №{data['number']} от {data['date']}"
            )
        
        # Отправка копии администратору
        if ADMIN_ID:
            try:
                admin_text = (
                    f"📄 <b>Новый документ создан!</b>\n\n"
                    f"Пользователь: @{callback.from_user.username} ({callback.from_user.id})\n"
                    f"Тип: {doc_name}\n"
                    f"№{data['number']} от {data['date']}\n"
                    f"Сумма: {data['amount']} ₽"
                )
                with open(pdf_path, "rb") as pdf_file:
                    await callback.bot.send_document(
                        chat_id=ADMIN_ID,
                        document=pdf_file,
                        caption=admin_text
                    )
            except Exception as e:
                print(f"Ошибка отправки админу: {e}")
        
        await callback.answer("Документ создан!")
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при создании документа: {e}")
    
    finally:
        await state.clear()
        form_data.pop(user_id, None)
        
        # Возвращаем главное меню
        from handlers.start import get_main_keyboard
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )


# Отмена создания
@router.callback_query(F.data == "cancel_create", StateFilter(DocumentForm.confirm))
async def cancel_create(callback: CallbackQuery, state: FSMContext):
    """Отмена создания документа"""
    
    await state.clear()
    form_data.pop(callback.from_user.id, None)
    
    from handlers.start import get_main_keyboard
    
    await callback.message.answer(
        "❌ Создание отменено",
        reply_markup=get_main_keyboard()
    )
    await callback.answer("Отменено")


# Команда отмены
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия"""
    
    current_state = await state.get_state()
    
    if current_state:
        await state.clear()
        form_data.pop(message.from_user.id, None)
        
        from handlers.start import get_main_keyboard
        
        await message.answer(
            "❌ Действие отменено",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("Нет активного действия для отмены")
