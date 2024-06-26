import pytest
import os

import requests
from requests import Data


@pytest.fixture(autouse=True)
def prepared_data():
    Data.token = requests.authorize("admin", "admin").json()["token"]
    Data.user = requests.add_user(Data.token, "user", "user").json()
    Data.record1 = requests.add_record(Data.token, 1, "test_header1", "test_body1").json()
    Data.record2 = requests.add_record(Data.token, 2, "test_header2", "test_body2").json()

    yield

    requests.reset_data()


@pytest.fixture(scope="session", autouse=True)
def clear_all():

    yield

    if os.path.exists("authorization.txt"):
        os.remove("authorization.txt")
    if os.path.exists("users.txt"):
        os.remove("users.txt")
    if os.path.exists("records.txt"):
        os.remove("records.txt")
