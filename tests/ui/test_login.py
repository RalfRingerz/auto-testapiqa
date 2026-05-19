"""UI E2E тесты страницы /login Playwright sync API

Кейсы:
    test_login_with_invalid_credentials_shows_error — smoke: баннер «Invalid email/password»
    test_login_valid_credentials_opens_home — regression: registered_account, ссылка Home видна
    test_signup_page_displays_registration_form — smoke: /signup
Page Object: LoginPage. При падении делается скриншот и URL через conftest в Аллюру
"""

import allure
import pytest

from pages.login_page import LoginPage


@allure.feature("UI авторизация")
@allure.story("Неверные учётные данные")
@pytest.mark.ui
@pytest.mark.smoke
def test_login_with_invalid_credentials_shows_error(page):
    login = LoginPage(page)
    with allure.step("Открытие /login"):
        login.open()
    with allure.step("Ввод невалидных кредов"):
        login.login("notfound_user@test.ru", "wrongpass777")
    with allure.step("Проверка текста ошибки на странице"):
        error = login.get_error_text()
    assert "invalid" in error.lower() or "password" in error.lower()


@allure.feature("UI авторизация")
@allure.story("Успешный вход")
@pytest.mark.ui
@pytest.mark.regression
def test_login_valid_credentials_opens_home(page, registered_account: dict[str, str]):
    login = LoginPage(page)
    with allure.step("Открытие страницы /login"):
        login.open()
    with allure.step("Ввод валидных учётных данных"):
        login.login(registered_account["email"], registered_account["password"])
    with allure.step("Проверка перехода на главную"):
        login.expect_on_home_after_login()


@allure.feature("UI авторизация")
@allure.story("Регистрация: форма signup")
@pytest.mark.ui
@pytest.mark.smoke
def test_signup_page_displays_registration_form(page):
    auth = LoginPage(page)
    with allure.step("Открытие /signup"):
        auth.open_signup()
    with allure.step("Виден заголовок и поля регистрации"):
        auth.expect_signup_form()
