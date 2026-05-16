from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import get_user_session_by_token
from app.db.session import SessionLocal
from app.models.user import User
from app.models.permission import Permission, UserPermission

security_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token_credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = token_credentials.credentials
    session = get_user_session_by_token(db, token)
    expires_at = session.expires_at if session else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not session or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
    user = session.user
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return user


def require_roles(*allowed_roles: str):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role is None or current_user.role.role_name not in allowed_roles:
            raise HTTPException(status_code=403, detail="User does not have permission to perform this action")
        return current_user

    return role_dependency


def require_permissions(*required_permissions: str):
    def permission_dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        # Admin role bypass
        if current_user.role and current_user.role.role_name == "admin":
            return current_user

        # collect role permissions
        role_perms = {p.permission_key for p in (current_user.role.permissions if current_user.role else [])}

        # collect user-level overrides
        overrides = db.query(UserPermission).filter(UserPermission.user_id == current_user.id).all()
        granted_overrides = set()
        denied_overrides = set()
        for o in overrides:
            permission = db.get(Permission, o.permission_id)
            if not permission:
                continue
            if o.granted:
                granted_overrides.add(permission.permission_key)
            else:
                denied_overrides.add(permission.permission_key)

        effective_perms = (role_perms | granted_overrides) - denied_overrides

        for rp in required_permissions:
            if rp not in effective_perms:
                raise HTTPException(status_code=403, detail="User does not have the required permission")
        return current_user

    return permission_dependency
