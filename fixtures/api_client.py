"""HTTP-клиент и модели ответов REST API testapiqa.com (e-commerce стенд)

Содержит:
    обёртку над requests.Session (PracticeApiClient): signup, login, orders CRUD
    Pydantic схемы для валидации JSON: UserSchema, OrderSchema, OrderLineItem 
    Исключения TestApiQaError, SignupConflictError, LoginFailedError (исключения с 400)
Эндпоинты:
    POST /api/signup, POST /api/login,
    POST /api/orders, GET /api/orders/{email}, DELETE /api/orders/{id}
Используется в API тестах и cross-layer сценариях (подготовка данных для UI)
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import requests
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)


class TestApiQaError(Exception):
    """Ошибка API TestAPIQA"""

    def __init__(self, message: str, status_code: int, response_body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class SignupConflictError(TestApiQaError):
    """Email уже зарегистрирован - ошибка 400"""


class LoginFailedError(TestApiQaError):
    """Неверные учётные данные - ошибка 400"""


class OrderLineItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    price: int | float | str
    quantity: int


class OrderSchema(BaseModel):
    """Ответ POST /api/orders и элементы GET /api/orders/{email}"""

    model_config = ConfigDict(extra="ignore")

    id: int
    user_email: str
    status: str
    items: list[OrderLineItem] = Field(default_factory=list)
    subtotal: int | float | str | None = None
    shipping: int | float | str | None = None
    total: int | float | str | None = None
    address: str | None = None
    date: str | None = None


class UserSchema(BaseModel):
    """Ответ /api/signup и /api/login при happy-path кейсе"""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    email: str
    firstName: str | None = None
    lastName: str | None = None


class PracticeApiClient:
    """Клиент к публичному API testapiqa.com"""

    def __init__(self, base_url: str, timeout: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = self._url(path)
        log.info("API %s %s", method, url)
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        log.info("API %s %s -> %s", method, url, resp.status_code)
        return resp

    def register(self, payload: dict[str, Any]) -> UserSchema:
        """POST /api/signup полный payload как у фронтенда стенда"""
        resp = self._request("POST", "/api/signup", json=payload)
        if resp.status_code == 400:
            try:
                body = resp.json()
            except requests.JSONDecodeError:
                body = resp.text
            err = body.get("error", "") if isinstance(body, dict) else str(body)
            if "already registered" in err.lower() or "login" in err.lower():
                raise SignupConflictError(err, resp.status_code, body)
            raise TestApiQaError(err or "signup failed", resp.status_code, body)
        resp.raise_for_status()
        return UserSchema.model_validate(resp.json())

    def login(self, email: str, password: str) -> UserSchema:
        """POST /api/login"""
        resp = self._request("POST", "/api/login", json={"email": email, "password": password})
        if resp.status_code == 400:
            try:
                body = resp.json()
            except requests.JSONDecodeError:
                body = resp.text
            err = body.get("error", "") if isinstance(body, dict) else str(body)
            raise LoginFailedError(err or "login failed", resp.status_code, body)
        resp.raise_for_status()
        return UserSchema.model_validate(resp.json())

    def create_order(
        self,
        *,
        user_email: str,
        items: list[dict[str, Any]],
        subtotal: int | float,
        shipping: int | float,
        total: int | float,
        address: str,
        status: str = "Processing",
    ) -> OrderSchema:
        """POST /api/orders (как checkout на сайте)"""
        payload = {
            "user_email": user_email,
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
            "address": address,
            "status": status,
        }
        resp = self._request("POST", "/api/orders", json=payload)
        resp.raise_for_status()
        return OrderSchema.model_validate(resp.json())

    def list_orders(self, user_email: str) -> list[OrderSchema]:
        """GET /api/orders/{email} список заказов пользователя"""
        safe = quote(user_email, safe="")
        resp = self._request("GET", f"/api/orders/{safe}")
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise TestApiQaError("expected list of orders", resp.status_code, data)
        return [OrderSchema.model_validate(item) for item in data]

    def delete_order(self, order_id: int) -> None:
        """DELETE /api/orders/{id}"""
        resp = self._request("DELETE", f"/api/orders/{order_id}")
        resp.raise_for_status()
