from fastapi import FastAPI, Header, status, Response

from typing import Annotated
from types import FunctionType

from users import BaseUser, User
from records import BaseRecord, Record

from databases import Users, Records, AuthList


server = FastAPI()
users = Users()
records = Records()
tokens = AuthList()


@server.post("/api/auth")
def authorize(data: BaseUser):
    user_id = users.get_user_id(data=data)
    answer_data = tokens.new_token(user_id=user_id) if isinstance(user_id, int) else user_id
    return answer_data


@server.post("/api/users")
def add_user(data: BaseUser, response: Response, token: Annotated[str or None, Header()] = None):
    status_code, answer_data = generate_response(func=users.add_user, data={"data": data}, token=token)
    response.status_code = status_code
    return answer_data


@server.get("/api/users/{id}")
def get_user(id: int, response: Response, token: Annotated[str or None, Header()] = None):
    status_code, answer_data = generate_response(func=users.get_user, data={"id": id}, token=token)
    response.status_code = status_code
    return answer_data


@server.get("/api/users")
def get_users_list():
    answer_data = {"data": [user.to_dict()["name"] for user in users.users_list]}
    return answer_data


@server.put("/api/users/{id}")
def change_user(id: int, data: BaseUser, response: Response, token: Annotated[str or None, Header()] = None):
    status_code, answer_data = generate_response(func=users.change_user, data={"id": id, "data": data}, token=token)
    response.status_code = status_code
    return answer_data


@server.post("/api/records")
def add_record(data: BaseRecord, response: Response, token: Annotated[str or None, Header()] = None):
    status_code, answer_data = generate_response(func=records.new_record, data={"data": data}, token=token)
    response.status_code = status_code
    return answer_data


@server.delete("/api/records/{id}")
def delete_record(id: int, response: Response, token: Annotated[str or None, Header()] = None):
    status_code, answer_data = generate_response(func=records.delete_record, data={"id": id, "user_id": tokens.get_user_id(token)}, token=token)
    response.status_code = status_code
    return answer_data


@server.put("/api/records/{id}")
def change_record(id: int, data: Record, response: Response, token: Annotated[str or None, Header()] = None):
    status_code, answer_data = generate_response(func=records.change_record, data={"id": id, "data": data}, token=token)
    response.status_code = status_code
    return answer_data


@server.get("/api/records/{id}")
def get_record(id: int):
    answer_data = records.get_record(id=id)
    return answer_data


@server.get("/api/records")
def get_records_list():
    answer_data = {"data": [record.to_dict() for record in records.records_list]}
    return answer_data


def generate_response(func: FunctionType, data: dict, token: str):
    if tokens.is_token_exist(token):
        result_data = func(**data)
        status_code = status.HTTP_200_OK
    else:
        result_data = {"error": "wrong token"}
        status_code = status.HTTP_401_UNAUTHORIZED
    return status_code, result_data