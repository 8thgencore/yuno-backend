from typing import Any

from fastapi import HTTPException, status


class UserSelfDeleteException(HTTPException):
    def __init__(
        self,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can not delete theirselfs.",
            headers=headers,
        )


class EmailNotFoundException(HTTPException):
    def __init__(
        self,
        email: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to find the user with an e-mail: {email}.",
            headers=headers,
        )
