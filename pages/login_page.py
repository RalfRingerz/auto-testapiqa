"""Page Object страниц входа /login и регистрации /signup

Сценарии: успешный логин, неверные креды, smoke формы регистрации
Используется в test_login.py и как шаг в E2E (корзина, cross layer заказы)
"""

from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"
    SIGNUP_URL = "/signup"

    EMAIL_INPUT = 'input[name="email"]'
    PASSWORD_INPUT = 'input[name="password"]'
    SUBMIT_BUTTON = "button.form-submit"

    def open(self) -> None:
        self.navigate(self.URL)

    def open_signup(self) -> None:
        self.navigate(self.SIGNUP_URL)

    def expect_signup_form(self) -> None:
        expect(self.page.get_by_role("heading", name="Create Account")).to_be_visible()
        expect(self.page.get_by_placeholder("Enter your full name")).to_be_visible()
        expect(self.page.get_by_placeholder("Enter your email")).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self.fill_input(self.EMAIL_INPUT, username)
        self.fill_input(self.PASSWORD_INPUT, password)
        self.click_when_ready(self.SUBMIT_BUTTON)

    def get_error_text(self) -> str:
        banner = self.page.locator(".auth-card-body").filter(has_text="Invalid email").first
        banner.wait_for(state="visible")
        return banner.text_content() or ""

    def expect_on_home_after_login(self) -> None:
        expect(self.page.get_by_role("link", name="Home").first).to_be_visible()
