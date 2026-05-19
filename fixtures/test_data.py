"""Генераторы тестовых payload для API testapiqa.com

Функции:
    signup_payload — полное тело POST /api/signup (поля формы регистрации на стенде),
    уникальный email auto_{uid}@mail.com, overrides через kwargs
    sample_order_item — позиция заказа для POST /api/orders (id, name, price, quantity)
Данные согласованы с фронтендом стенда. Cлучайные части нужны для изоляции тестов
"""

from __future__ import annotations

import random
import string
from typing import Any


def _random_str(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def sample_order_item(product_id: int = 1, name: str = "Blue Top", price: int = 500, quantity: int = 1) -> dict[str, Any]:
    """Позиция заказа в формате, который принимает POST /api/orders"""
    return {"id": product_id, "name": name, "price": price, "quantity": quantity}


def signup_payload(**overrides: Any) -> dict[str, Any]:
    """Тело POST /api/signup (поля как у формы регистрации на стенде)"""
    uid = _random_str(10)
    email = f"auto_{uid}@mail.com"
    base: dict[str, Any] = {
        "name": f"Auto User {uid}",
        "email": email,
        "password": "TestPass123!",
        "firstName": "Auto",
        "lastName": "Test",
        "company": "QA Russia",
        "address": "1 Krasnaya Street",
        "address2": "",
        "country": "Russia",
        "state": "Moscow",
        "city": "Moscow",
        "zipcode": "9379992",
        "mobile": "+7995" + "".join(str(random.randint(0, 9)) for _ in range(7)),
    }
    base.update(overrides)
    return base
