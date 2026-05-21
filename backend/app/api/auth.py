from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.deps import get_db, security_scheme, get_current_user
from app.core.security import create_user_session, get_user_session_by_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutResponse, TokenResponse
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(form_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    device_info = f"{request.client.host if request.client else 'unknown'}"
    token, _ = create_user_session(db, user, device_info=device_info)
    
    # Manually construct user data to avoid serialization issues
    user_data = UserRead(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role_name=user.role_name,
        is_active=user.is_active
    )
    
    return TokenResponse(access_token=token, user=user_data)



@router.get("/me", response_model=TokenResponse)
def whoami(current_user: User = Depends(get_current_user)):
    # Manually construct user data to avoid serialization issues
    user_data = UserRead(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role_name=current_user.role_name,
        is_active=current_user.is_active
    )
    return TokenResponse(access_token="", user=user_data)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    token_credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    session = get_user_session_by_token(db, token_credentials.credentials)
    if session:
        db.delete(session)
        db.commit()
    return LogoutResponse(detail="Successfully logged out")
