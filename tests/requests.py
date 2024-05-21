from fastapi.testclient import TestClient
from server import server


client = TestClient(server)


class Data:
    token: str
    user: dict
    record1: dict
    record2: dict


def authorize(name, passwd):
    response = client.post("/api/auth",
                           json={"name": name, "password": passwd})
    return response


def add_user(token, name, passwd):
    response = client.post("/api/users",
                           headers={"token": token},
                           json={"name": name, "password": passwd})
    return response


def get_user(token, user_id):
    response = client.get(f"api/users/{user_id}",
                          headers={"token": token})
    return response


def change_user(token, user_id, name, passwd):
    response = client.put(f"/api/users/{user_id}",
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


def change_record(token, record_id, user_id, header, body):
    response = client.put(f"/api/records/{record_id}",
                          headers={"token": token},
                          json={
                              "user_id": user_id,
                              "header": header,
                              "body": body
                          })
    return response


def get_record(record_id):
    response = client.get(f"api/records/{record_id}")
    return response


def delete_record(token, record_id):
    response = client.delete(f"api/records/{record_id}",
                             headers={"token": token})
    return response


def reset_data():
    response = client.put("/wipe")
    return response
