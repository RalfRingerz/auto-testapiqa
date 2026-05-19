"""Page Object каталога товаров /products 

Поиск по плейсхолдеру, фильтр "All Products", открытие первой карточки через "Select Size"
Поддержка эндпоинта /products/men как фильтра категории "Men"
"""

from playwright.sync_api import expect

from pages.base_page import BasePage


class CatalogPage(BasePage):
    """Каталог товаров: URL, селекторы карточек и поиска."""

    URL = "/products"
    URL_MEN_PRODUCTS = "/products/men"

    SEARCH_INPUT = 'input[placeholder="Search for products..."]'
    SEARCH_BUTTON = ".search-bar button"
    PRODUCT_CARD = ".product-card"
    PRODUCT_TITLE = f"{PRODUCT_CARD} .product-name"
    PRODUCT_CATEGORY_TAG = ".product-category-tag"
    ALL_PRODUCTS_CATEGORY = ".sidebar-category-item"

    def open(self) -> None:
        self.navigate(self.URL)

    def open_men_products(self) -> None:
        """Мужская линейка: надёжнее прямого URL, чем клик по сайдбару. Нет целевого элемента с текстом "Men" """
        self.navigate(self.URL_MEN_PRODUCTS)

    def fill_search_query(self, query: str) -> None:
        self.fill_input(self.SEARCH_INPUT, query)

    def submit_search(self) -> None:
        self.click_when_ready(self.SEARCH_BUTTON)

    def search_product(self, query: str) -> None:
        self.fill_search_query(query)
        self.submit_search()

    def select_all_products_category(self) -> None:
        self.select_category("All Products")

    def select_category(self, category_name: str) -> None:
        sidebar = self.page.locator(self.ALL_PRODUCTS_CATEGORY)
        exact = category_name == "Men"
        label_locator = self.page.get_by_text(category_name, exact=exact)
        sidebar.filter(has=label_locator).first.click()

    def expect_first_product_name_contains(self, text: str) -> None:
        title = self.page.locator(self.PRODUCT_TITLE).first
        expect(title).to_be_visible()
        expect(title).to_contain_text(text)

    def get_first_product_name(self) -> str:
        title = self.page.locator(self.PRODUCT_TITLE).first
        title.wait_for(state="visible")
        return (title.inner_text() or "").strip()

    def expect_all_product_cards_are_men_category_line(self) -> None:
        """Выдача только мужских вещей, и ни одной карточки Women"""
        cards = self.page.locator(self.PRODUCT_CARD)
        expect(cards.first).to_be_visible()
        n = cards.count()
        assert n >= 1, "После поиска должна быть хотя бы одна карточка"

        women_cards = self.page.locator(self.PRODUCT_CARD).filter(
            has=self.page.locator(self.PRODUCT_CATEGORY_TAG).filter(has_text="Women —"),
        )
        expect(women_cards).to_have_count(0)

        for i in range(n):
            tag = cards.nth(i).locator(self.PRODUCT_CATEGORY_TAG)
            expect(tag).to_be_visible()
            expect(tag).to_contain_text("Men —", ignore_case=True)

    def open_first_product_vs_select_size(self) -> None:
        card = self.page.locator(self.PRODUCT_CARD).first
        card.wait_for(state="visible")
        card.get_by_role("link", name="Select Size").click()
