"""
Модели данных
Описание структур данных для работы с БД
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Модель пользователя"""
    id: int
    user_id: int
    username: Optional[str]
    created_at: datetime
    
    @classmethod
    def from_row(cls, row: dict):
        """Создание модели из строки БД"""
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            created_at=row["created_at"]
        )


@dataclass
class Document:
    """Модель документа"""
    id: int
    user_id: int
    doc_type: str  # 'invoice' или 'act'
    number: str
    date: str
    description: str
    amount: float
    payer: str
    file_path: Optional[str]
    created_at: datetime
    
    @property
    def type_name(self) -> str:
        """Человекочитаемое название типа"""
        return "Счёт" if self.doc_type == "invoice" else "Акт"
    
    @property
    def amount_formatted(self) -> str:
        """Отформатированная сумма"""
        return f"{self.amount:,.2f} ₽".replace(",", " ")
    
    @classmethod
    def from_row(cls, row: dict):
        """Создание модели из строки БД"""
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            doc_type=row["doc_type"],
            number=row["number"],
            date=row["date"],
            description=row["description"],
            amount=row["amount"],
            payer=row["payer"],
            file_path=row["file_path"],
            created_at=row["created_at"]
        )
