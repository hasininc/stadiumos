from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserResponse, LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth import AuthService
from app.api.deps import get_db, get_current_user
from app.models.auth import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register_user(user_in)

@router.post("/login", response_model=TokenResponse)
def login(login_in: LoginRequest, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.authenticate_user(login_in)
    
    # Store refresh token in secure HTTP-only cookie for client CSRF defense
    response.set_cookie(
        key="stadiumos_refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=7 * 24 * 3600,
        secure=True,
        samesite="strict"
    )
    return tokens

@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.refresh_access_token(refresh_token)
    
    # Rotate refresh token cookie
    response.set_cookie(
        key="stadiumos_refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=7 * 24 * 3600,
        secure=True,
        samesite="strict"
    )
    return tokens

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(refresh_token: str, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.revoke_token(refresh_token)
    response.delete_cookie(key="stadiumos_refresh_token")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(req: ForgotPasswordRequest):
    # Mocking email notification system trigger
    return {"message": "Recovery verification email has been dispatched"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(req: ResetPasswordRequest):
    # Mocking password update logic
    return {"message": "Password credentials reset successfully"}
