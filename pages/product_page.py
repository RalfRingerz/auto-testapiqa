"""Page Object карточки товара /product/{id} 

Выбор размера в блоке "Select Size:" (если есть), Add to Cart, проверка заголовка
Используется после перехода из каталога в E2E сценариях корзины
"""

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    """Карточка товара /product/{id}"""

    def _size_buttons(self) -> Locator:
        return (
            self.page.get_by_text("Select Size:", exact=False)
            .locator("..")
            .get_by_role("button", disabled=False)
        )

    def select_first_available_size_if_present(self) -> str | None:
        """Первый доступный размер в блоке Select Size, если блок есть на странице"""
        try:
            expect(self.page.get_by_text("Select Size:", exact=False)).to_be_visible()
        except AssertionError:
            return None

        size_btn = self._size_buttons().first
        expect(size_btn).to_be_visible()
        expect(size_btn).to_be_enabled()
        size = (size_btn.inner_text() or "").strip()
        size_btn.click()
        return size or None

    def add_to_cart(self) -> None:
        btn = self.page.get_by_role("button", name="Add to Cart")
        expect(btn).to_be_enabled()
        btn.click()

    def expect_product_title(self, title: str) -> None:
        expect(self.page.get_by_role("heading", level=1, name=title)).to_be_visible()
