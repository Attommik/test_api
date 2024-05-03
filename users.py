from pydantic import BaseModel


class BaseUser(BaseModel):
    name: str
    password: str


class User(BaseUser):
    id: int = -1
    name: str = ""
    password: str = ""

    def to_dict(self):
        return {"id": self.id, "name": self.name, "password": self.password}

    def from_dict(self, user: dict):
        self.id = user.get("id")
        self.name = user.get("name")
        self.password = user.get("password")
        return self

    def change_name(self, name: str):
        self.name = name

    def change_password(self, password: str):
        self.password = password


