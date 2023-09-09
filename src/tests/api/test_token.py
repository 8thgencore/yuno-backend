import pytest

from app.core.security import create_access_token, create_refresh_token, create_reset_token


@pytest.mark.usefixtures(scope="module")
def get_access_token():
    return create_access_token("testuser")


@pytest.mark.usefixtures(scope="module")
def get_refresh_token():
    return create_refresh_token("testuser")


@pytest.mark.usefixtures(scope="module")
def get_reset_token():
    return create_reset_token("testuser")
