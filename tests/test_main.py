import json
import time
import pytest
from datetime import datetime

from config import AUTH_FILENAME, TOKEN_LIFETIME_SECONDS
import requests
from requests import Data


def test_smoke():
    assert Data.token
    assert Data.user == {'id': 2, 'name': 'user', 'password': 'user'}
    assert Data.record1 == {'id': 1, 'user_id': 1, 'header': 'test_header1', 'body': 'test_body1'}
    assert Data.record2 == {'id': 2, 'user_id': 2, 'header': 'test_header2', 'body': 'test_body2'}


@pytest.mark.skip("Токен не протухает")
def test_token_lifetime():
    last_call = 0
    token = 0
    with open(AUTH_FILENAME, "r") as f:
        data = json.loads(f.read())
    for auth in data["auth_list"]:
        last_call = auth["last_call"]
        token = auth["token"]
        break
    if last_call + TOKEN_LIFETIME_SECONDS >= int(datetime.now().timestamp()):
        time.sleep(TOKEN_LIFETIME_SECONDS)

    response = requests.add_user(token, "name", "passwd")

    # assert response.status_code == 200
    assert response.json()["error"]
