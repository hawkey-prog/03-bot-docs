"""
Генератор PDF-документов
Создание счетов и актов с помощью библиотеки reportlab
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config import TEMP_DIR


async def generate_invoice_pdf(data: dict, user_id: int) -> str:
    """
    Генерация PDF счёта на оплату
    
    Args:
        data: Данные счёта (number, date, description, amount, payer)
        user_id: ID пользователя
    
    Returns:
        Путь к созданному файлу
    """
    
    # Создаем папку для временных файлов
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Имя файла
    filename = f"invoice_{user_id}_{data['number']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(TEMP_DIR, filename)
    
    # Создание документа
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Заголовок
    elements.append(Paragraph("СЧЁТ НА ОПЛАТУ", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Информация о счёте
    info_data = [
        [f"Счёт № {data['number']}", f"Дата: {data['date']}"],
    ]
    
    info_table = Table(info_data, colWidths=[9*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))
    
    # Таблица с товаром/услугой
    elements.append(Paragraph("Наименование товара/услуги:", styles['Heading3']))
    elements.append(Spacer(1, 0.3*cm))
    
    items_data = [
        ['№', 'Наименование', 'Кол-во', 'Цена', 'Сумма'],
        ['1', data['description'], '1', f"{data['amount']:.2f} ₽", f"{data['amount']:.2f} ₽'],
        ['', '', '', 'Итого:', f"{data['amount']:.2f} ₽'],
    ]
    
    items_table = Table(items_data, colWidths=[1*cm, 10*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 1*cm))
    
    # Плательщик
    payer_data = [
        ['Плательщик:', data['payer']],
    ]
    
    payer_table = Table(payer_data, colWidths=[4*cm, 14*cm])
    payer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    elements.append(payer_table)
    elements.append(Spacer(1, 2*cm))
    
    # Подписи
    signature_data = [
        ['Исполнитель:', '_________________ / _________________ /'],
    ]
    
    signature_table = Table(signature_data, colWidths=[4*cm, 14*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    elements.append(signature_table)
    
    # Построение документа
    doc.build(elements)
    
    return filepath


async def generate_act_pdf(data: dict, user_id: int) -> str:
    """
    Генерация PDF акта выполненных работ
    
    Args:
        data: Данные акта (number, date, description, amount, payer)
        user_id: ID пользователя
    
    Returns:
        Путь к созданному файлу
    """
    
    # Создаем папку для временных файлов
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Имя файла
    filename = f"act_{user_id}_{data['number']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(TEMP_DIR, filename)
    
    # Создание документа
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Заголовок
    elements.append(Paragraph("АКТ ВЫПОЛНЕННЫХ РАБОТ", title_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Номер и дата
    number_date = f"№ {data['number']} от {data['date']}"
    elements.append(Paragraph(number_date, styles['Normal']))
    elements.append(Spacer(1, 1*cm))
    
    # Текст акта
    act_text = f"""
    <b>Исполнитель</b> выполнил работы для <b>Заказчика</b> {data['payer']}:
    <br/><br/>
    {data['description']}
    <br/><br/>
    Работы выполнены в полном объёме и в установленный срок.
    Заказчик не имеет претензий к качеству и срокам выполнения работ.
    <br/><br/>
    <b>Стоимость работ:</b> {data['amount']:.2f} ₽
    """
    
    elements.append(Paragraph(act_text, styles['Normal']))
    elements.append(Spacer(1, 2*cm))
    
    # Таблица подписей
    signature_data = [
        ['Исполнитель:', '_________________', 'Заказчик:', '_________________'],
        ['', '', '', data['payer']],
    ]
    
    signature_table = Table(signature_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(signature_table)
    
    # Построение документа
    doc.build(elements)
    
    return filepath
