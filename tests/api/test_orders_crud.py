"""API тесты жизненного цикла заказов POST /api/orders 

Фикстура registered_account изолирует пользователя с email для GET
Эндпоинты: POST /api/orders, GET /api/orders/{email}, DELETE /api/orders/{id}
Кейсы:
    test_order_create_list_delete — smoke: создание, наличие в списке, удаление, отсутствие после DELETE
    test_list_orders_new_user_empty — regression: у свежего пользователя список заказов пуст
"""

import pytest
import allure

from fixtures.api_client import PracticeApiClient
from fixtures.test_data import sample_order_item


@allure.feature("API заказы")
@allure.story("Создание, список и удаление")
@allure.severity("critical")
@pytest.mark.api
@pytest.mark.smoke
def test_order_create_list_delete(api_client: PracticeApiClient, registered_account: dict[str, str]):
    email = registered_account["email"]
    item = sample_order_item()
    subtotal = 500
    shipping = 0
    total = 500

    with allure.step("POST /api/orders создание заказа"):
        created = api_client.create_order(
            user_email=email,
            items=[item],
            subtotal=subtotal,
            shipping=shipping,
            total=total,
            address="1 API Test St",
        )
    assert created.id > 0
    assert created.user_email == email

    with allure.step("GET /api/orders заказ есть в списке"):
        orders = api_client.list_orders(email)
        ids = [o.id for o in orders]
        assert created.id in ids

    with allure.step("DELETE /api/orders/{id}"):
        api_client.delete_order(created.id)

    with allure.step("Повторный GET /api/orders — удалённого заказа нет в списке"):
        after = api_client.list_orders(email)
        assert created.id not in [o.id for o in after]


@allure.feature("API заказы")
@allure.story("Пустой список у нового пользователя")
@pytest.mark.api
@pytest.mark.regression
def test_list_orders_new_user_empty(api_client: PracticeApiClient, registered_account: dict[str, str]):
    """Сразу после регистрации заказов нет. Негативный сценарий с пустым списком"""
    with allure.step("GET /api/orders — пустой список"):
        orders = api_client.list_orders(registered_account["email"])
    assert orders == []
