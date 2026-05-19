"""UI E2E сценарии корзины: от логина до очистки 

Цепочка: LoginPage - CatalogPage - ProductPage - CartPage
Кейсы:
    test_guest_cart_is_empty — smoke: гость на /cart видит пустую корзину
    test_cart_add_product_and_remove — regression: добавление с размером, Remove, пустая корзина
    test_cart_remove_vs_minus_should_empty_cart — xfail: кнопка "−" не очищает корзину (известный баг)
Требует registered_account. изоляция данных через нового пользователя на тест.
"""

import allure
import pytest

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage


@allure.feature("UI корзина")
@allure.story("Гость: пустая корзина")
@pytest.mark.ui
@pytest.mark.smoke
def test_guest_cart_is_empty(page):
    cart = CartPage(page)
    with allure.step("Открытие /cart без авторизации"):
        cart.open()
    with allure.step("Корзина пуста"):
        cart.expect_empty()


@allure.feature("UI корзина")
@allure.story("Добавление и удаление товара")
@pytest.mark.ui
@pytest.mark.regression
def test_cart_add_product_and_remove(page, registered_account: dict[str, str]):
    login = LoginPage(page)
    catalog = CatalogPage(page)
    product_page = ProductPage(page)
    cart = CartPage(page)

    with allure.step("Логин зарегистрированным пользователем"):
        login.open()
        login.login(registered_account["email"], registered_account["password"])
        login.expect_on_home_after_login()

    with allure.step("Каталог: категория All Products и первый товар"):
        catalog.open()
        catalog.select_all_products_category()
        product_name = catalog.get_first_product_name()
        catalog.open_first_product_vs_select_size()

    with allure.step("Карточка товара: выбор размера и добавление в корзину"):
        product_page.expect_product_title(product_name)
        selected_size = product_page.select_first_available_size_if_present()
        product_page.add_to_cart()

    with allure.step("Корзина: проверка добавленного товара"):
        cart.open()
        cart.expect_product(product_name, selected_size)

    with allure.step("Удаление товара кнопкой «Remove»"):
        cart.remove_product(product_name)
        cart.expect_empty()


@allure.feature("UI корзина")
@allure.story("Удаление через кнопку МИНУС")
@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(reason="Кнопка МИНУС не очищает корзину", strict=True)
def test_cart_remove_vs_minus_should_empty_cart(page, registered_account: dict[str, str]):
    """Кнопка МИНУС не удаляет позицию. xfail, баг не исправлен"""
    login = LoginPage(page)
    catalog = CatalogPage(page)
    product_page = ProductPage(page)
    cart = CartPage(page)

    with allure.step("Вход зарегистрированным пользователем"):
        login.open()
        login.login(registered_account["email"], registered_account["password"])
        login.expect_on_home_after_login()

    with allure.step("Каталог: категория «Все товары» и первый товар"):
        catalog.open()
        catalog.select_all_products_category()
        product_name = catalog.get_first_product_name()
        catalog.open_first_product_vs_select_size()

    with allure.step("Карточка товара: выбор размера и добавление в корзину"):
        product_page.expect_product_title(product_name)
        product_page.select_first_available_size_if_present()
        product_page.add_to_cart()

    with allure.step("Корзина: уменьшение количества кнопкой МИНУС"):
        cart.open()
        cart.remove_product_vs_minus(product_name)

    with allure.step("Проверка: корзина пуста после уменьшения количества до нуля"):
        cart.expect_empty()
