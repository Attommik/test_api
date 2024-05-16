import pytest
import requests


class TestAuthorize:
    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("admin", "admin"),
            ("user", "user")
        ]
    )
    def test_authorize(self, name, passwd):
        response = requests.authorize(name, passwd)

        assert response.status_code == 200
        assert response.json()["token"]

    @pytest.mark.parametrize(
        "name, passwd",
        [
            ("user111", "user"),
            ("admin", "admin111"),
            ("admin", ""),
            ("", "")
        ]
    )
    def test_authorize_negative(self, name, passwd):
        response = requests.authorize(name, passwd)

        # assert response.status_code == 200
        assert response.json()["error"]
