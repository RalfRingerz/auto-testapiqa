"""UI /orders и cross layer: заказ через API виден в браузере

    test_guest_orders_requires_login — smoke: без логина блок «Please Login»
    test_cross_layer_order_visible_in_ui — regression: signup + API order + видимость в UI
"""

import re

import allure
import pytest
from playwright.sync_api import expect

from fixtures.api_client import PracticeApiClient
from fixtures.test_data import sample_order_item, signup_payload
from pages.login_page import LoginPage
from pages.orders_page import OrdersPage


@allure.feature("UI заказы")
@allure.story("Гость: только после логина")
@pytest.mark.ui
@pytest.mark.smoke
def test_guest_orders_requires_login(page):
    orders = OrdersPage(page)
    with allure.step("Открытие /orders без авторизации"):
        orders.open()
    with allure.step("Отображается приглашение войти"):
        orders.expect_login_required()


@allure.feature("Сквозной сценарий")
@allure.story("Заказ через API отображается в UI")
@allure.severity("critical")
@pytest.mark.ui
@pytest.mark.regression
def test_cross_layer_order_visible_in_ui(page, api_client: PracticeApiClient):
    with allure.step("Регистрация пользователя через API"):
        payload = signup_payload()
        api_client.register(payload)
    email, password = payload["email"], payload["password"]

    with allure.step("Создание заказа через API"):
        created = api_client.create_order(
            user_email=email,
            items=[sample_order_item(name="CrossLayer Item", price=400, quantity=1)],
            subtotal=400,
            shipping=0,
            total=400,
            address="API Cross St",
        )

    login = LoginPage(page)
    orders = OrdersPage(page)
    with allure.step("UI логин и переход в My Orders"):
        login.open()
        login.login(email, password)
        expect(page).to_have_url(re.compile(r"https?://[^/]+/?$"))
        orders.open()

    with allure.step("На странице заказов виден OrderID из API"):
        orders.expect_order_visible(created.id)
