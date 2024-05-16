import pytest
import requests
from requests import Data


class TestUserAdd:

    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("user 1!", "user 1!")
        ]
    )
    def test_add_user(self, name, passwd):
        response = requests.add_user(Data.token, name, passwd)
        user_id = response.json()["id"]

        assert response.status_code == 200
        assert requests.get_user(Data.token, user_id).json() == {
            "id": user_id,
            "name": name,
            "password": passwd
        }

    @pytest.mark.skip("Создает пользователя с пустым полем имени и/или пароля")
    @pytest.mark.parametrize(
        "token, name, passwd",
        [
            (-1, "admin", "admin"),
            ("132313", "user", "user"),
            ("132313", "test", "test"),
            ("", "user", "user"),
            (" ", "test", "test"),
            (-1, "test", ""),
            (-1, "test1", " "),
            (-1, "", "test"),
            (-1, " ", "test1"),
            (-1, "", ""),
            (-1, " ", " ")
        ]
    )
    def test_add_user_negative(self, token, name, passwd):
        if token == -1:
            token = Data.token
        response = requests.add_user(token, name, passwd)

        # assert response.status_code == 200
        assert response.json()["error"]


class TestChangeUser:
    def test_change_user(self):
        user_id, name, passwd = 2, "useruser", "useruser"
        response = requests.change_user(Data.token, user_id, name, passwd)

        assert response.status_code == 200
        assert requests.get_user(Data.token, user_id).json() == {
            "id": user_id,
            "name": name,
            "password": passwd
        }

    @pytest.mark.skip("Сохраняет пользователя с пустым полем имени и/или пароля")
    @pytest.mark.parametrize(
        "token, user_id, name, passwd",
        [
            (-1, -2, "adm", "adm"),
            (-1, 0, "adm", "adm"),
            (-1, 100, "adm", "adm"),
            (-1, " ", "adm", "adm"),
            ("123", 1, "adm", "adm"),
            ("", 1, "adm", "adm"),
            (" ", 2, "adm", "adm"),
            (-1, 1, "", "adm"),
            (-1, 1, "adm", ""),
            (-1, 1, "", "")
        ]
    )
    def test_change_user_negative(self, token, user_id, name, passwd):
        if token == -1:
            token = Data.token
        response = requests.change_user(token, user_id, name, passwd)

        # assert response.status_code == 200
        assert response.json()["error"]
