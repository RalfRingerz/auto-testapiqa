"""Page Object "Мои заказы" /orders после авторизации 

Отображение карточек заказов (.order-card) с номером #{order_id}
Используется в cross layer сценарии: заказ создан через API, проверка видимости на фронте
"""

from playwright.sync_api import expect

from pages.base_page import BasePage


class OrdersPage(BasePage):
    """Мои заказы /orders после логина"""

    URL = "/orders"

    ORDER_CARD = ".order-card"
    ORDER_ID_VALUE = ".order-id-value"

    def open(self) -> None:
        self.navigate(self.URL)

    def expect_login_required(self) -> None:
        expect(self.page.get_by_text("Please Login to View Orders")).to_be_visible()

    def expect_order_visible(self, order_id: int) -> None:
        expect(self.page.locator(self.ORDER_CARD).filter(has_text=f"#{order_id}")).to_be_visible()
