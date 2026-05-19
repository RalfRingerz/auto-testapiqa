"""Page Object корзины /cart 

Проверка позиций (.cart-item), удаление через Remove или кнопку − (минус)
expect_empty: сообщение "Your cart is empty"
покрывает test_cart_flow.py, в т.ч. xfail на баг с минусом
"""

from playwright.sync_api import expect

from pages.base_page import BasePage


class CartPage(BasePage):
    """Корзина /cart"""

    URL = "/cart"
    CART_ITEM = ".cart-item"

    def open(self) -> None:
        self.navigate(self.URL)

    def open_from_header(self) -> None:
        self.page.get_by_role("link", name="Cart 1").click()

    def expect_product(self, product_name: str, size: str | None = None) -> None:
        item = self.page.locator(self.CART_ITEM).filter(has_text=product_name)
        expect(item).to_be_visible()
        expect(item).to_contain_text(product_name)
        if size:
            expect(item).to_contain_text(size)

    def remove_product(self, product_name: str) -> None:
        item = self.page.locator(self.CART_ITEM).filter(has_text=product_name)
        item.get_by_role("button", name="Remove").click()

    def remove_product_vs_minus(self, product_name: str) -> None:
        item = self.page.locator(self.CART_ITEM).filter(has_text=product_name)
        item.get_by_role("button", name="−").click()

    def expect_empty(self) -> None:
        expect(self.page.get_by_text("Your cart is empty")).to_be_visible()
