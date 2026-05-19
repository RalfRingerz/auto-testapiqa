"""API-тесты авторизации POST /api/login 

Кейсы:
    test_login_returns_user — smoke: логин после registered_account, проверка id и email
    test_login_invalid_credentials_api — regression: 400 и LoginFailedError на невалидный пароль

Маркеры: @pytest.mark.api, smoke/regression. Отчётность: Allure feature "API авторизация"
"""

import pytest
import allure

from fixtures.api_client import LoginFailedError, PracticeApiClient


@allure.feature("API авторизация")
@allure.story("Успешный вход")
@allure.severity("blocker")
@pytest.mark.api
@pytest.mark.smoke
def test_login_returns_user(api_client: PracticeApiClient, registered_account: dict[str, str]):
    with allure.step("POST /api/login после регистрации"):
        user = api_client.login(registered_account["email"], registered_account["password"])
    assert user.id > 0
    assert user.email == registered_account["email"]


@allure.feature("API авторизация")
@allure.story("Неверные учётные данные")
@pytest.mark.api
@pytest.mark.regression
def test_login_invalid_credentials_api(api_client: PracticeApiClient):
    with allure.step("POST /api/login с неверным паролем"):
        with pytest.raises(LoginFailedError) as exc:
            api_client.login("notfound_user@test.ru", "wrongpass777")
    assert exc.value.status_code == 400
    assert "invalid" in str(exc.value).lower() or "password" in str(exc.value).lower()
