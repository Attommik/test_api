from pydantic import BaseModel
from datetime import datetime, timedelta
from uuid import uuid4
from config import TOKEN_LIFETIME_SECONDS


class UserAuth(BaseModel):
    user_id: int = -1
    token: str = ""
    last_call: int = 0

    def from_dict(self, record: dict):
        self.user_id = record["user_id"]
        self.token = record["token"]
        self.last_call = record["last_call"]
        return self

    def to_dict(self):
        return {"user_id": self.user_id, "token": self.token, "last_call": self.last_call}

    def new(self, user_id):
        self.user_id = user_id
        self.token = str(uuid4())
        self.last_call = int(datetime.now().timestamp())
        return self

    def refresh(self):
        self.last_call = int(datetime.now().timestamp())

    def check(self, user_id, token):
        return self.user_id == user_id and self.token == token

    def is_expired(self):
        return self.last_call > int(datetime.now().timestamp()) - TOKEN_LIFETIME_SECONDS