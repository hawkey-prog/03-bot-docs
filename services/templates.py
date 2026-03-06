"""
Шаблоны документов
Текстовые шаблоны для счетов и актов
"""

# Шаблон счёта на оплату
INVOICE_TEMPLATE = """
СЧЁТ НА ОПЛАТУ № {number}
Дата: {date}

Плательщик: {payer}

Наименование товара/услуги: {description}

Сумма: {amount} ₽

Исполнитель: _________________ / _________________ /
"""

# Шаблон акта выполненных работ
ACT_TEMPLATE = """
АКТ ВЫПОЛНЕННЫХ РАБОТ
№ {number} от {date}

Исполнитель выполнил работы для Заказчика {payer}:

{description}

Работы выполнены в полном объёме и в установленный срок.
Заказчик не имеет претензий к качеству и срокам выполнения работ.

Стоимость работ: {amount} ₽

Исполнитель: _________________
Заказчик: _________________ / {payer} /
"""

# Шаблон для сообщения подтверждения
CONFIRM_TEMPLATE = """
📋 Проверьте данные документа:

📄 Тип: {doc_type}
🔢 Номер: {number}
📅 Дата: {date}
📦 Описание: {description}
💰 Сумма: {amount} ₽
🏢 {counterparty_type}: {payer}

Всё верно?
"""


def get_invoice_text(data: dict) -> str:
    """Получение текста счёта"""
    return INVOICE_TEMPLATE.format(**data)


def get_act_text(data: dict) -> str:
    """Получение текста акта"""
    return ACT_TEMPLATE.format(**data)


def get_confirm_text(data: dict, doc_type: str) -> str:
    """Получение текста подтверждения"""
    counterparty = "Плательщик" if doc_type == "invoice" else "Заказчик"
    doc_name = "Счёт" if doc_type == "invoice" else "Акт"
    
    return CONFIRM_TEMPLATE.format(
        doc_type=doc_name,
        counterparty_type=counterparty,
        **data
    )
