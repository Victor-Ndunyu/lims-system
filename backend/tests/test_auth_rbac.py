from app.models.permission import Permission, UserPermission


def login_token(client, email, password="password"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_auth_me_returns_current_user(client, seed_data):
    token = login_token(client, "field_officer@example.com")

    response = client.get("/api/auth/me", headers=auth_header(token))
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["access_token"] == ""
    assert payload["user"]["email"] == "field_officer@example.com"
    assert payload["user"]["full_name"] == "field_officer user"


def test_inactive_user_cannot_login(client, db, seed_data):
    user = seed_data["users"]["field_officer"]
    user.is_active = False
    db.commit()

    response = client.post("/api/auth/login", json={"email": user.email, "password": "password"})
    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


def test_admin_can_create_and_list_users(client, seed_data):
    token = login_token(client, "admin@example.com")
    headers = auth_header(token)

    create_response = client.post(
        "/api/admin/users",
        json={"full_name": "New Staff", "email": "new.staff@example.com", "password": "secretpass", "role_name": "field_officer"},
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text
    assert create_response.json()["email"] == "new.staff@example.com"

    list_response = client.get("/api/admin/users", headers=headers)
    assert list_response.status_code == 200, list_response.text
    emails = [user["email"] for user in list_response.json()]
    assert "new.staff@example.com" in emails


def test_user_permission_override_allows_manage_users_actions(client, db, seed_data):
    reviewer = seed_data["users"]["reviewer"]
    target_user = seed_data["users"]["field_officer"]

    permission = Permission(permission_key="manage_users", description="Manage users")
    db.add(permission)
    db.commit()
    db.refresh(permission)

    override = UserPermission(user_id=reviewer.id, permission_id=permission.id, granted=True)
    db.add(override)
    db.commit()

    reviewer_token = login_token(client, "reviewer@example.com")
    response = client.post(
        f"/api/admin/users/{target_user.id}/permissions",
        json=[{"permission_key": "manage_users", "granted": True}],
        headers=auth_header(reviewer_token),
    )
    assert response.status_code == 200, response.text
    assert response.json()["detail"] == "User permission overrides updated"


def test_admin_role_required_for_admin_endpoints(client, seed_data):
    field_token = login_token(client, "field_officer@example.com")
    response = client.get("/api/admin/users", headers=auth_header(field_token))
    assert response.status_code == 403
    assert response.json()["detail"] == "User does not have permission to perform this action"
