from users import BaseUser, User
from records import BaseRecord, Record
from authorization import UserAuth

import json

from config import USERS_FILENAME, RECORDS_FILENAME, AUTH_FILENAME


def singletone(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singletone
class Users:
    current_id: int = 0
    users_list: list = []

    def __init__(self):
        try:
            self._load_from_file()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.current_id = 0
            self.users_list = []
        if not self.users_list:
            self.add_user(data=BaseUser(name="admin", password="admin"))

    def _save_to_file(func, **kwargs):
        def inner(self, **kwargs):
            result = func(self, **kwargs)
            with open(USERS_FILENAME, "w") as f:
                data = {"current_id": self.current_id, "users_list": [u.dict() for u in self.users_list]}
                f.write(json.dumps(data))
            return result
        return inner

    def _load_from_file(self):
        with open(USERS_FILENAME, "r") as f:
            data = json.loads(f.read())
        self.current_id = data["current_id"]
        self.users_list = [User().from_dict(u) for u in data["users_list"]]

    @_save_to_file
    def add_user(self, data: BaseUser):
        name_exists = False
        for user in self.users_list:
            if user.name == data.name:
                name_exists = True
                break
        if not name_exists:
            self.current_id += 1
            self.users_list.append(User(id=self.current_id, name=data.name, password=data.password))
            return self.users_list[-1].to_dict()
        return {"error": f"user {data.name} is already exist"}

    def get_user(self, id):
        for user in self.users_list:
            if user.id == id:
                return user.to_dict()
        return {"error": f"user with {id=} does not exist"}

    def get_user_id(self, data: BaseUser):
        for user in self.users_list:
            if data.name ==user.name and data.password == user.password:
                return user.id
        return {"error": "wrong user or password"}

    @_save_to_file
    def change_user(self, id: int, data: BaseUser):
        changed = None
        for user in self.users_list:
            if id == user.id:
                user.change_name(name=data.name)
                user.change_password(password=data.password)
                changed = user
        if changed:
            return changed.to_dict()
        return {"error": f"user with {id=} does not exist"}

    def reset(self):
        with open(USERS_FILENAME, "w"):
            pass
        self.__init__()


@singletone
class Records:
    current_id: int = 0
    records_list: list = []

    def __init__(self):
        try:
            self._load_from_file()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.current_id = 0
            self.records_list = []

    def _save_to_file(func, **kwargs):
        def inner(self, **kwargs):
            result = func(self, **kwargs)
            with open(RECORDS_FILENAME, "w") as f:
                data = {"current_id": self.current_id, "records_list": [r.dict() for r in self.records_list]}
                f.write(json.dumps(data))
            return result
        return inner

    def _load_from_file(self):
        with open(RECORDS_FILENAME, "r") as f:
            data = json.loads(f.read())
        self.current_id = data["current_id"]
        self.records_list = [Record().from_dict(record) for record in data["records_list"]]

    @_save_to_file
    def new_record(self, data: BaseRecord):
        self.current_id += 1
        self.records_list.append(Record(id=self.current_id, user_id=data.user_id, header=data.header, body=data.body))
        return self.records_list[-1].to_dict()

    @_save_to_file
    def delete_record(self, id: int, user_id):
        record_finded = False
        mark_to_delete = False
        for record in self.records_list:
            if record.id == id:
                if user_id == record.user_id:
                    result = {}
                    record_finded = True
                    mark_to_delete = True
                else:
                    result = {"error": f"record with {id=} belongs to another user"}
                    record_finded = True
        if mark_to_delete:
            self.records_list = [record for record in self.records_list if record.id!=id]
        if record_finded:
            return result
        return {"error": f"record with {id=} does not exist"}

    @_save_to_file
    def change_record(self, id: int, data: BaseRecord):
        changed = False
        for record in self.records_list:
            if record.id == id and data.user_id == record.user_id:
                result = record.change(data).to_dict()
            changed = True
        if not changed:
            result = {"error": f"there is no record with {id=} belongs to user with id={data.user_id}"}
        return result

    def get_record(self, id: int):
        for record in self.records_list:
            if record.id == id:
                return record.to_dict()
        return {"error": f"there is no record with {id=}"}

    def reset(self):
        with open(RECORDS_FILENAME, "w"):
            pass
        self.__init__()


@singletone
class AuthList:
    auth_list: list = []

    def _save_to_file(func, **kwargs):
        def inner(self, **kwargs):
            result = func(self, **kwargs)
            with open(AUTH_FILENAME, "w") as f:
                data = {"auth_list": [auth.to_dict() for auth in self.auth_list]}
                f.write(json.dumps(data))
            return result
        return inner

    def _load_from_file(self):
        with open(AUTH_FILENAME, "r") as f:
            data = json.loads(f.read())
        self.auth_list = [UserAuth().from_dict(auth) for auth in data["auth_list"]]

    def __init__(self):
        try:
            self._load_from_file()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.auth_list = []

    @_save_to_file
    def new_token(self, user_id: int):
        auth = UserAuth().new(user_id=user_id)
        self.auth_list.append(auth)
        return {"token": auth.token}

    def is_token_exist(self, token):
        for auth in self.auth_list:
            if auth.token == token:
                return True
        return False

    def get_user_id(self, token):
        if self.is_token_exist(token):
            for auth in self.auth_list:
                if auth.token == token:
                    return auth.user_id
        return -1

    def reset(self):
        with open(AUTH_FILENAME, "w"):
            pass
        self.__init__()
