"""API тесты граничных сценариев заказов

Кейс test_list_orders_unknown_email_returns_empty:
    GET /api/orders/{email} для несуществующего email — ожидается 200 и []
Не создаёт пользователя в БД. email генерируется через uuid для уникальности
Маркер: @pytest.mark.api, regression
"""

import uuid

import allure
import pytest

from fixtures.api_client import PracticeApiClient


@allure.feature("API заказы")
@allure.story("Список для неизвестного email")
@pytest.mark.api
@pytest.mark.regression
def test_list_orders_unknown_email_returns_empty(api_client: PracticeApiClient):
    """Для несуществующего email API возвращается 200 и пустой список заказов"""
    ghost = f"ghost_{uuid.uuid4().hex[:10]}@no-user.mail.com"
    with allure.step(f"GET /api/orders для несуществующего email ({ghost})"):
        orders = api_client.list_orders(ghost)
    assert orders == []
