from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class UserNotCreatorProject(HTTPException):
    def __init__(
        self,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not the creator this project",
            headers=headers,
        )


class UserNotMemberProject(HTTPException):
    def __init__(
        self,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not a member of this project",
            headers=headers,
        )


class UserAlredyMemberProject(HTTPException):
    def __init__(
        self,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is already a member of this project",
            headers=headers,
        )
