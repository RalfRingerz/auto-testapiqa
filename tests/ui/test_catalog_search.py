"""UI каталог /products: поиск и категория Men

    test_products_search_shows_cards — smoke: поиск «Top», карточки на экране
    test_catalog_men_category_filters_products — regression: /products/men, первый товар мужской линейки
    test_products_search_men_only_men_categories — карточки только MEN
"""

import allure
import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage


@allure.feature("UI каталог")
@allure.story("Поиск товаров")
@allure.severity("normal")
@pytest.mark.ui
@pytest.mark.smoke
def test_products_search_shows_cards(page):
    catalog = CatalogPage(page)
    with allure.step("Открытие каталога /products"):
        catalog.open()
    with allure.step("Поиск по ключевому слову «Top»"):
        catalog.search_product("Top")
    with allure.step("Проверка наличия карточек товаров"):
        cards = page.locator(".product-card")
        expect(cards.first).to_be_visible()
        assert cards.count() >= 1


@allure.feature("UI каталог")
@allure.story("Категория Men")
@pytest.mark.ui
@pytest.mark.regression
def test_catalog_men_category_filters_products(page):
    catalog = CatalogPage(page)
    with allure.step("Открытие каталога мужской линейки (/products/men)"):
        catalog.open_men_products()
    with allure.step("Первый товар — сегмент Men (название содержит Men)"):
        catalog.expect_first_product_name_contains("Men")


@allure.feature("UI каталог")
@allure.story("Поиск men: только мужская линейка")
@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(reason="Поиск смешивает men и women в выдаче", strict=False)
def test_products_search_men_only_men_categories(page):
    """Корректная выдача: по запросу men не должно быть карточек Women. Сейчас на стенде — смешение, тест падает."""
    catalog = CatalogPage(page)
    with allure.step("/products — ввод 'men' "):
        catalog.open()
        catalog.fill_search_query("men")
    with allure.step("Клик Search"):
        catalog.submit_search()
    with allure.step("Только мужская линейка: 0 карточек WOMEN, у всех есть MEN"):
        catalog.expect_all_product_cards_are_men_category_line()
