from httpx import AsyncClient


async def test_register(ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password",
        },
    )
    data = response.json()["data"]

    assert response.status_code == 201
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


async def test_login(ac: AsyncClient):
    response = await ac.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password",
        },
    )
    data = response.json()["data"]

    assert response.status_code == 200
    assert "access_token" in data
    assert "refresh_token" in data


# async def test_change_password(ac: AsyncClient):
#     access_token = get_access_token()
#     response = await ac.post(
#         "/auth/change-password",
#         json={
#             "current_password": "password",
#             "new_password": "newpassword",
#         },
#         headers={"Authorization": f"Bearer {access_token}"},
#     )
#     assert response.status_code == 200


# async def test_forgot_password(ac: AsyncClient):
#     response = await ac.post(
#         "/auth/forgot-password",
#         json={
#             "email": "test@example.com",
#         },
#     )
#     assert response.status_code == 202


# async def test_reset_password(ac: AsyncClient):
#     reset_token = get_reset_token()
#     response = await ac.post(
#         "/auth/reset-password",
#         json={
#             "reset_token": reset_token,
#             "password": "newpassword",
#         },
#     )
#     assert response.status_code == 200
