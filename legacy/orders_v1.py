"""Пример устаревшего кода Pydantic v1 (этап 1) — только для сравнения."""
from datetime import datetime

from pydantic import BaseModel, validator


class Order(BaseModel):
    id: int
    customer_email: str
    total: float
    status: str = "new"
    created_at: datetime = None

    @validator("customer_email")
    def check_email(cls, v):
        if "@" not in v:
            raise ValueError("invalid email")
        return v

    @validator("total")
    def check_total(cls, v):
        if v <= 0:
            raise ValueError("total must be > 0")
        return v

    class Config:
        orm_mode = True


def order_to_dict(order):
    return order.dict()


def order_to_json(order):
    return order.json()
