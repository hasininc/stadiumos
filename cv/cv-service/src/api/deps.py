from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from src.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

ALGORITHM = "HS256"

def get_current_user_roles(token: str = Depends(oauth2_scheme)) -> list[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token type credentials",
            )
        roles = payload.get("roles", [])
        return roles
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials signature",
            headers={"WWW-Authenticate": "Bearer"},
        )

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, roles: list[str] = Depends(get_current_user_roles)) -> list[str]:
        # Allow administrators bypass checks
        if "Administrator" in roles:
            return roles

        for role in self.allowed_roles:
            if role in roles:
                return roles

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions scope to access this computer vision node.",
        )
