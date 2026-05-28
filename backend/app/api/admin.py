from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, selectinload
from typing import List

from app.core.deps import get_db, get_current_user, require_roles, require_permissions
from app.core.security import hash_password
from app.core.audit import log_audit
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission, UserPermission
from app.models.sample import Sample
from app.models.audit_log import AuditLog
from app.schemas.user import UserRead, UserCreate, UserUpdate, RoleRead, PermissionRead
from sqlalchemy import func
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserRead], dependencies=[Depends(require_roles("admin"))])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.full_name).all()
    return users


@router.post("/users", response_model=UserRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_user(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    role = None
    if user_in.role_name:
        role = db.query(Role).filter(Role.role_name == user_in.role_name).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid role")

    user = User(full_name=user_in.full_name, email=user_in.email, password_hash=hash_password(user_in.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit(db=db, table_name="users", record_id=str(user.id), action="create", old_values=None, new_values={"email": user.email, "full_name": user.full_name}, performed_by=None, ip_address=request.client.host if request.client else None)
    return user


@router.patch("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles("admin"))])
def update_user(user_id: str, user_in: UserUpdate, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_values = {"email": user.email, "full_name": user.full_name, "is_active": user.is_active}

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None:
        user.password_hash = hash_password(user_in.password)
    if user_in.role_name is not None:
        role = db.query(Role).filter(Role.role_name == user_in.role_name).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid role")
        user.role = role
    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    db.commit()
    db.refresh(user)

    log_audit(db=db, table_name="users", record_id=str(user.id), action="update", old_values=old_values, new_values={"email": user.email, "full_name": user.full_name, "is_active": user.is_active}, performed_by=None, ip_address=request.client.host if request.client else None)
    return user


@router.delete("/users/{user_id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if str(user.id) == str(current_user.id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot delete yourself")
    log_audit(db=db, table_name="users", record_id=str(user.id), action="delete", old_values={"email": user.email, "full_name": user.full_name}, new_values=None, performed_by=str(current_user.id), ip_address=request.client.host if request.client else None)
    db.delete(user)
    db.commit()


@router.post("/roles", response_model=RoleRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_role(role: RoleRead, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.role_name == role.role_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")
    r = Role(role_name=role.role_name, description=role.description)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/roles", response_model=List[RoleRead], dependencies=[Depends(require_roles("admin"))])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).options(selectinload(Role.permissions)).order_by(Role.role_name).all()


@router.post("/permissions", response_model=PermissionRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_permission(p_in: PermissionRead, db: Session = Depends(get_db)):
    existing = db.query(Permission).filter(Permission.permission_key == p_in.permission_key).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission already exists")
    p = Permission(permission_key=p_in.permission_key, description=p_in.description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/permissions", response_model=List[PermissionRead], dependencies=[Depends(require_roles("admin"))])
def list_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).order_by(Permission.permission_key).all()


@router.post("/roles/{role_id}/permissions", dependencies=[Depends(require_permissions("manage_users"))])
def assign_permissions_to_role(role_id: str, permission_keys: List[str], db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    perms = db.query(Permission).filter(Permission.permission_key.in_(permission_keys)).all()
    role.permissions = perms
    db.commit()
    return {"detail": "Permissions assigned"}


@router.post("/users/{user_id}/permissions", dependencies=[Depends(require_permissions("manage_users"))])
def set_user_permissions(user_id: str, overrides: List[dict], db: Session = Depends(get_db)):
    """Overrides is a list of {permission_key: str, granted: bool}. This replaces existing overrides for the user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # remove existing
    db.query(UserPermission).filter(UserPermission.user_id == user.id).delete()
    db.commit()

    for o in overrides:
        perm = db.query(Permission).filter(Permission.permission_key == o.get("permission_key")).first()
        if not perm:
            continue
        up = UserPermission(user_id=user.id, permission_id=perm.id, granted=bool(o.get("granted", True)))
        db.add(up)
    db.commit()
    return {"detail": "User permission overrides updated"}


@router.get("/stats", dependencies=[Depends(require_roles("admin"))])
def dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    inactive_users = total_users - active_users
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    records_today = db.query(Sample).filter(Sample.created_at >= today_start).count()
    pending_approvals = db.query(Sample).filter(Sample.status == "Submitted").count()
    published = db.query(Sample).filter(Sample.status == "Approved").count()

    recent_activity = (
        db.query(AuditLog)
        .order_by(AuditLog.performed_at.desc())
        .limit(20)
        .all()
    )

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "records_submitted_today": records_today,
        "pending_approvals": pending_approvals,
        "published_records": published,
        "recent_activity": [
            {"action": r.action, "table": r.table_name, "performed_by": str(r.performed_by) if r.performed_by else None, "at": r.performed_at.isoformat()} for r in recent_activity
        ],
    }


@router.get("/charts", dependencies=[Depends(require_roles("admin"))])
def charts_data(db: Session = Depends(get_db)):
    # Simple chart data endpoints that can be expanded. Use SQL for aggregation.
    from sqlalchemy import func as sa_func

    records_by_status = (
        db.query(Sample.status, sa_func.count(Sample.id))
        .group_by(Sample.status)
        .all()
    )

    records_by_type = (
        db.query(Sample.sample_type_id, sa_func.count(Sample.id))
        .group_by(Sample.sample_type_id)
        .all()
    )

    users_by_role = (
        db.query(Role.role_name, sa_func.count(User.id))
        .join(User, User.role_id == Role.id)
        .group_by(Role.role_name)
        .all()
    )

    return {
        "records_by_status": [{"status": s, "count": c} for s, c in records_by_status],
        "records_by_type": [{"sample_type_id": str(t), "count": c} for t, c in records_by_type],
        "users_by_role": [{"role": r, "count": c} for r, c in users_by_role],
    }
