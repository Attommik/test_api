import json
import time

import pytest
from datetime import datetime
from config import AUTH_FILENAME, TOKEN_LIFETIME_SECONDS
import requests
from requests import client, Data


def test_smoke():
    assert Data.token
    assert Data.user == {'id': 2, 'name': 'user', 'password': 'user'}
    assert Data.record1 == {'id': 1, 'user_id': 1, 'header': 'test_header1', 'body': 'test_body1'}


class TestAuthorize:
    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("admin", "admin"),
            ("user", "user")
        ]
    )
    def test_authorize(self, name, passwd):
        response = requests.authorize(name, passwd)

        assert response.status_code == 200
        assert response.json()["token"]

    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("user111", "user"),
            ("admin", "admin111"),
            ("", "")
        ]
    )
    def test_authorize_negative(self, name, passwd):
        response = requests.authorize(name, passwd)

        # assert response.status_code == 200
        assert response.json()["error"]


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

    @pytest.mark.skip()
    @pytest.mark.parametrize(
        "token, name, passwd",
        [
            (-1 , "admin", "admin"),
            ("132313", "user", "user"),
            ("132313", "test", "test"),
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
        user_id, name, passwd = 1, "adm", "adm"
        response = requests.change_user(Data.token, user_id, name, passwd)
        # assert response.status_code == 200
        assert response.json() == {
            "id": user_id,
            "name": name,
            "password": passwd
        }

    @pytest.mark.skip
    @pytest.mark.parametrize(
        "token, user_id, name, passwd",
        [
            (-1, -2, "adm", "adm"),
            (-1, 0, "adm", "adm"),
            (-1, 100, "adm", "adm"),
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


def test_change_record():
    requests.change_record(Data.token, Data.record1["id"], Data.record1["user_id"], "head1", "body1")

    assert requests.get_record(Data.record1["id"]).json() == {
        "id": Data.record1["id"],
        "user_id": 1,
        "header": "head1",
        "body": "body1"
    }


@pytest.mark.skip
@pytest.mark.parametrize(
    "token, header, body, user_id",
    [
        ("111", "head", "body", 1),
        ("", "head", "body", 1),
        (-1, "head", "body", 2),
        (-1, "head", "body", 100)
    ]
)
def test_change_record_negative(token, header, body, user_id, prepared_data):
    record_id = prepared_data["record1"]["id"]
    if token == -1:
        token = prepared_data["token"]
    response = client.put(f"/api/records/{record_id}",
                          headers={"token": token},
                          json={
                              "user_id": user_id,
                              "header": header,
                              "body": body
                          })

    assert response.json()["error"]


def test_delete_record(prepared_data):
    response = client.delete(f"api/records/{prepared_data["record1"]["id"]}",
                             headers={"token": prepared_data["token"]})

    assert response.json() == {}
    # print(response.json())


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
def test_delete_record_negative(token, record_id, prepared_data):
    if token == -1:
        token = prepared_data["token"]
    response = client.delete(f"api/records/{record_id}",
                             headers={"token": token})

    assert response.json()["error"]
    print(response.json())
    print(client.get("api/records").json())


@pytest.mark.parametrize(
    "token, header, body, user_id",
    [
        (-1, "head", "body", 1),
        (-1, "", "body", 1),
        (-1, "head", "", 1),
        (-1, "", "", 1),
    ]
)
def test_add_record(token, header, body, user_id, prepared_data):
    if token == -1:
        token = prepared_data["token"]
    response = requests.add_record(token, user_id, header, body)

    assert response.status_code == 200
    # print((response.json()))


@pytest.mark.skip
@pytest.mark.parametrize(
    "token, header, body, user_id",
    [
        ("", "head", "body", 1),
        ("111", "head", "body", 1),
        (-1, "head", "body", -99)
    ]
)
def test_add_record_negative(header, body, token, user_id, prepared_data):
    if token == -1:
        token = prepared_data["token"]
    response = client.post("/api/records",
                           headers={"token": token},
                           json={
                               "user_id": user_id,
                               "header": header,
                               "body": body
                           })
    assert response.json()["error"]
    # print(response.json())


def test_token_lifetime(prepared_data):
    last_call = 0
    token = 0
    with open(AUTH_FILENAME, "r") as f:
        data = json.loads(f.read())
    for auth in data["auth_list"]:
        last_call = auth["last_call"]
        token = auth["token"]
        break
    # if last_call + TOKEN_LIFETIME_SECONDS >= int(datetime.now().timestamp()):
    #     time.sleep(TOKEN_LIFETIME_SECONDS)

    response = requests.add_user(token, "name", "passwd")
    user_id = response.json()["id"]
    assert response.status_code == 200
    assert requests.get_user(token, user_id).json() == {
               "id": user_id,
               "name": "name",
               "password": "passwd"
           }
