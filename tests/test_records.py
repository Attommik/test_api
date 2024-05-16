import pytest
import requests
from requests import Data


class TestAddRecord:

    @pytest.mark.parametrize(
        "token, user_id, header, body",
        [
            (-1, 1, "head", "body"),
            (-1, 1, "", "body"),
            (-1, 1, "head", ""),
            (-1, 1, "", "")
        ]
    )
    def test_add_record(self, token, user_id, header, body):
        if token == -1:
            token = Data.token
        response = requests.add_record(token, user_id, header, body)

        assert response.status_code == 200

    @pytest.mark.skip("Создает запись от имени другого пользователя")
    @pytest.mark.parametrize(
        "token, user_id, header, body",
        [
            ("", 1, "head", "body"),
            ("111", 1, "head", "body"),
            (-1, -99, "head", "body")
        ]
    )
    def test_add_record_negative(self, token, user_id, header, body):
        if token == -1:
            token = Data.token
        response = requests.add_record(token, user_id, header, body)

        assert response.json()["error"]


class TestChangeRecord:
    def test_change_record(self):
        response = requests.change_record(Data.token, Data.record1["id"], Data.record1["user_id"], "head1", "body1")

        assert response.status_code == 200
        assert requests.get_record(Data.record1["id"]).json() == {
            "id": Data.record1["id"],
            "user_id": Data.record1["user_id"],
            "header": "head1",
            "body": "body1"
        }

    @pytest.mark.skip("Не обработано исключение при попытке изменить id владельца записи")
    @pytest.mark.parametrize(
        "token, user_id, header, body",
        [
            ("111", 1, "head", "body"),
            ("", 1, "head", "body"),
            (-1, 2, "head", "body"),
            (-1, 100, "head", "body")
        ]
    )
    def test_change_record_negative(self, token, user_id, header, body):
        if token == -1:
            token = Data.token
        response = requests.change_record(token, Data.record1["id"], user_id, header, body)

        assert response.json()["error"]


class TestDeleteRecord:
    def test_delete_record(self):
        response = requests.delete_record(Data.token, Data.record1["id"])

        assert response.status_code == 200
        assert response.json() == {}

    @pytest.mark.parametrize(
        "token, record_id",
        [
            (-1, -3),
            (-1, 30),
            (-1, 2),
            (-1, "2"),
            ("", 1)
        ]
    )
    def test_delete_record_negative(self, token, record_id):
        if token == -1:
            token = Data.token
        response = requests.delete_record(token, record_id)

        assert response.json()["error"]
