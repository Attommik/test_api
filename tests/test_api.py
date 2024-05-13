import json
import pytest
import os
from fastapi.testclient import TestClient
from datetime import datetime
from server import server
from config import AUTH_FILENAME, TOKEN_LIFETIME_SECONDS


client = TestClient(server)


def authorize(name, passwd):
    response = client.post("/api/auth",
                           json={"name": name, "password": passwd})

    return response


def add_user(token, name, passwd):
    response = client.post("/api/users",
                           headers={"token": token},
                           json={"name": name, "password": passwd})

    return response


def add_record(token, user_id, header, body):
    response = client.post("/api/records",
                           headers={"token": token},
                           json={
                               "user_id": user_id,
                               "header": header,
                               "body": body
                           })

    return response


@pytest.fixture(scope="module")
def prepared_data():
    token = authorize("admin", "admin").json()["token"]
    user = add_user(token, "user", "user").json()
    record1 = add_record(token, 1, "test_header1", "test_body1").json()
    record2 = add_record(token, 2, "test_header2", "test_body2").json()

    yield {"token": token, "user": user, "record1": record1, "record2": record2}

    if os.path.exists("authorization.txt"):
        os.remove("authorization.txt")
    if os.path.exists("users.txt"):
        os.remove("users.txt")
    if os.path.exists("records.txt"):
        os.remove("records.txt")


def test_smoke(prepared_data):
    assert prepared_data["token"]
    assert prepared_data["user"] == {'id': 2, 'name': 'user', 'password': 'user'}
    assert prepared_data["record1"] == {'id': 1, 'user_id': 1, 'header': 'test_header1', 'body': 'test_body1'}


class TestAuthorize:
    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("admin", "admin"),
            ("user", "user")
        ]
    )
    def test_authorize(self, name, passwd, prepared_data):
        response = client.post("/api/auth",
                               json={"name": name, "password": passwd})

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
    def test_authorize_negative(self, name, passwd, prepared_data):
        response = client.post("/api/auth",
                               json={"name": name, "password": passwd})

        # assert response.status_code == 200
        assert response.json()["error"]


class TestUserAdd:

    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("user 1!", "user 1!")
        ]
    )
    def test_add_user(self, name, passwd, prepared_data):
        response = add_user(prepared_data["token"], name, passwd)
        user_id = response.json()["id"]
        assert response.status_code == 200
        assert client.get(f"api/users/{user_id}",
                          headers={"token": prepared_data["token"]}).json() == {
            "id": user_id,
            "name": name,
            "password": passwd
        }

    @pytest.mark.skip
    @pytest.mark.parametrize(
        "token, name, passwd",
        [
            (-1, "admin", "admin"),
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
    def test_add_user_negative(self, token, name, passwd, prepared_data):
        if token == -1:
            token = prepared_data["token"]
        response = add_user(token, name, passwd)

        # assert response.status_code == 200
        assert response.json()["error"]


class TestChangeUser:
    def test_change_user(self, prepared_data):
        user_id, name, passwd = 1, "adm", "adm"
        response = client.put(f"/api/users/{user_id}",
                              headers={"token": prepared_data["token"]},
                              json={"name": name, "password": passwd})
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
    def test_change_user_negative(self, token, user_id, name, passwd, prepared_data):
        if token == -1:
            token = prepared_data["token"]
        response = client.put(f"/api/users/{user_id}",
                              headers={"token": token},
                              json={"name": name, "password": passwd})
        # assert response.status_code == 200
        assert response.json()["error"]


def test_change_record(prepared_data):
    record_id = prepared_data["record1"]["id"]
    client.put(f"/api/records/{record_id}",
               headers={"token": prepared_data["token"]},
               json={
                   "user_id": 1,
                   "header": "head1",
                   "body": "body1"
               })

    assert client.get(f"api/records/{record_id}").json() == {
        "id": record_id,
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
        (-1, 3),
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
    # print(client.get("api/records").json())


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
    response = add_record(token, user_id, header, body)

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
    while last_call + TOKEN_LIFETIME_SECONDS >= int(datetime.now().timestamp()):
        continue

    response = add_user(token, "name", "passwd")
    user_id = response.json()["id"]
    assert response.status_code == 200
    assert client.get(f"api/users/{user_id}",
                      headers={"token": token}).json() == {
               "id": user_id,
               "name": "name",
               "password": "passwd"
           }
