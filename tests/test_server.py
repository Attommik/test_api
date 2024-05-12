import json
import pytest
import os
from fastapi.testclient import TestClient
from datetime import datetime
from server import server
from config import AUTH_FILENAME, TOKEN_LIFETIME_SECONDS


@pytest.fixture(scope="module", autouse=True)
def clear():
    yield

    if os.path.exists("authorization.txt"):
        os.remove("authorization.txt")
    if os.path.exists("users.txt"):
        os.remove("users.txt")
    if os.path.exists("records.txt"):
        os.remove("records.txt")


@pytest.fixture()
def expired_token():
    exp_token = 0
    with open(AUTH_FILENAME, "r") as f:
        data = json.loads(f.read())
    for auth in data["auth_list"]:
        if auth["last_call"] + TOKEN_LIFETIME_SECONDS < int(datetime.now().timestamp()):
            exp_token = [auth["token"]]
        break

    return exp_token


# @pytest.fixture(scope="module", autouse=True)
def authorize():
    response = client.post("/api/auth",
                           json={"name": "admin", "password": "admin"})

    return response.json()["token"]


def add_user(name, passwd, user_token):
    return client.post("/api/users",
                       headers={"token": str(user_token)},
                       json={"name": name, "password": passwd})


def add_record(header, body, user_token, user_id):
    return client.post("/api/records",
                       headers={"token": str(user_token)},
                       json={
                           "user_id": user_id,
                           "header": header,
                           "body": body
                       })


client = TestClient(server)
token = authorize()


class TestAuthorize:
    def test_authorize(self):
        response = client.post("/api/auth",
                               json={"name": "admin", "password": "admin"})

        assert response.status_code == 200
        assert response.json()["token"]

    # @pytest.mark.parametrize(
    #     "name, passwd",
    #     [
    #         ("user", "user"),
    #         ("adm1n", "admin"),
    #         ("", "")
    #     ]
    # )
    # def test_authorize_negative(self, name, passwd):
    #     response = client.post("/api/auth",
    #                            json={"name": name, "password": passwd})
    #
    #     assert response.status_code == 200
    #     assert response.json()["error"]


class TestUserAdd:
    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("user", "user"),
            ("user 1!", "user 1!")
        ]
    )
    def test_add_user(self, name, passwd):
        response = add_user(name, passwd, token)

        assert response.status_code == 200
        assert response.json() == {
            "id": response.json()["id"],
            "name": name,
            "password": passwd
        }

    # @pytest.mark.parametrize(
    #     "name, passwd",
    #     [
    #         ("user", "user"),
    #         ("", "test"),
    #         (" ", "test1"),
    #         ("test", ""),
    #         ("test1", " "),
    #         ("", ""),
    #         (" ", " ")
    #     ]
    # )
    # def test_add_user_negative(self, name, passwd):
    #     response = add_user(name, passwd, token)
    #
    #     assert response.status_code == 200
    #     assert response.json()["error"]


class TestChangeUser:
    def test_change_user(self):
        user_id, name, passwd = 1, "adm", "adm"
        response = client.put(f"/api/users/{user_id}",
                              headers={"token": token},
                              json={"name": name, "password": passwd})
        assert response.status_code == 200
        assert response.json() == {
            "id": user_id,
            "name": name,
            "password": passwd
        }

    # @pytest.mark.parametrize(
    #     "user_id, name, passwd",
    #     [
    #         (2, "adm", "adm"),
    #         (-2, "adm", "adm"),
    #         (1, "", "adm"),
    #         (1, "adm", ""),
    #         (1, "", "")
    #     ]
    # )
    # def test_change_user_negative(self, user_id, name, passwd):
    #     response = client.put(f"/api/users/{user_id}",
    #                           headers={"token": token},
    #                           json={"name": name, "password": passwd})
    #     assert response.status_code == 200
    #     print(response.json())
    #     assert response.json()["error"]


# def test_get_users_list():
#     response = client.get("/api/users")
#     assert response.status_code == 200
#     assert response.json() == {"data": ["admin", "user", "qe"]}
#     print(response.json())


@pytest.mark.parametrize(
    "header, body, user_token, user_id",
    [
        ("head", "body", token, 1),
        ("", "body", token, 1),
        ("head", "", token, 1),
        ("", "", token, 1),
    ]
)
def test_add_record(header, body, user_token, user_id):
    response = client.post("/api/records",
                           headers={"token": user_token},
                           json={
                               "user_id": user_id,
                               "header": header,
                               "body": body
                           })
    assert response.status_code == 200


@pytest.mark.parametrize(
    "header, body, user_token, user_id",
    [
        ("head", "body", "", 1),
        ("head", "body", "111", 1),
        ("head", "body", token, -99)
    ]
)
def test_add_record_negative(header, body, user_token, user_id):
    response = client.post("/api/records",
                           headers={"token": user_token},
                           json={
                               "user_id": user_id,
                               "header": header,
                               "body": body
                           })
    assert response.json()["error"]


def test_delete_record():
    record = add_record("head", "body", token, 1).json()
    response = client.delete(f"api/records/{record["id"]}",
                             headers={"token": token})
    assert response.json() == {}
    print(record)


def test_delete_record_negative():
    record = add_record("head", "body", token, 2).json()
    response = client.delete(f"api/records/{record["id"]}",
                             headers={"token": token})
    assert response.json()["error"]


@pytest.mark.parametrize("")
def test_change_record():
    record = add_record("head", "body", token, 1).json()
    response = client.put(f"/api/records/{record["id"]}",
                          headers={"token": token},
                          json={
                              "user_id": 8,
                              "header": "head1",
                              "body": "body1"
                            })
