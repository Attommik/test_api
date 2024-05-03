from pydantic import BaseModel


class BaseRecord(BaseModel):
    user_id: int
    header: str
    body: str


class Record(BaseRecord):
    id: int = -1
    user_id: int = -1
    header: str = ""
    body: str = ""

    def from_dict(self, record):
        self.id = record["id"]
        self.user_id = record["user_id"]
        self.header = record["header"]
        self.body = record["body"]
        return self

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "header": self.header, "body": self.body}

    def change(self, record: BaseRecord):
        self.user_id = record.user_id
        self.header = record.header
        self.body = record.body
        return self
