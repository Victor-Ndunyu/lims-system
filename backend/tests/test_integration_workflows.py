from app.models.audit_log import AuditLog
from app.models.sample_version import SampleVersion


def login_token(client, email, password="password"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def sample_payload(seed_data, sample_code="SAMPLE-001", status="Draft"):
    return {
        "sample_code": sample_code,
        "sample_type_id": str(seed_data["sample_type"].id),
        "collection_date": "2026-05-11T00:00:00Z",
        "collector_id": str(seed_data["users"]["field_officer"].id),
        "location_id": str(seed_data["location"].id),
        "description": "Initial sample record",
        "remarks": "First submission",
        "status": status,
        "attachments": [
            {
                "file_name": "result.pdf",
                "file_type": "application/pdf",
                "file_url": "https://example.com/result.pdf",
            }
        ],
    }


def create_sample(client, seed_data, token, sample_code="SAMPLE-001", status="Draft"):
    response = client.post(
        "/api/staff/samples",
        json=sample_payload(seed_data, sample_code=sample_code, status=status),
        headers=auth_header(token),
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_authentication_login_logout_and_bad_credentials(client, seed_data):
    token = login_token(client, "field_officer@example.com")

    protected_response = client.get("/api/staff/samples", headers=auth_header(token))
    assert protected_response.status_code == 200

    logout_response = client.post("/api/auth/logout", headers=auth_header(token))
    assert logout_response.status_code == 200
    assert logout_response.json()["detail"] == "Successfully logged out"

    revoked_response = client.get("/api/staff/samples", headers=auth_header(token))
    assert revoked_response.status_code == 401

    bad_login = client.post(
        "/api/auth/login",
        json={"email": "field_officer@example.com", "password": "wrong-password"},
    )
    assert bad_login.status_code == 401


def test_authorization_enforces_staff_and_reviewer_roles(client, seed_data):
    field_token = login_token(client, "field_officer@example.com")

    unauthenticated = client.get("/api/staff/samples")
    assert unauthenticated.status_code == 403

    review_response = client.post(
        "/api/staff/samples/00000000-0000-0000-0000-000000000000/review",
        json={"decision": "Rejected", "comments": "Not allowed"},
        headers=auth_header(field_token),
    )
    assert review_response.status_code == 403


def test_sample_creation_sets_draft_defaults_and_audit_entries(client, db, seed_data):
    field_token = login_token(client, "field_officer@example.com")

    create_response = client.post(
        "/api/staff/samples",
        json=sample_payload(seed_data, sample_code=" SAMPLE-CREATE "),
        headers={**auth_header(field_token), "X-Forwarded-For": "203.0.113.20"},
    )
    assert create_response.status_code == 200, create_response.text
    sample = create_response.json()

    assert sample["status"] == "Draft"
    assert sample["sample_code"] == "SAMPLE-CREATE"
    assert sample["verification_status"] == "Draft"
    assert sample["public_visibility"] is False
    assert len(sample["attachments"]) == 1

    audit_entry = db.query(AuditLog).filter(AuditLog.record_id == sample["id"]).one()
    assert audit_entry.action == "create"
    assert audit_entry.table_name == "samples"
    assert audit_entry.old_values is None
    assert audit_entry.ip_address == "203.0.113.20"
    assert audit_entry.new_values["sample_code"] == "SAMPLE-CREATE"

    version = db.query(SampleVersion).filter(SampleVersion.sample_id == sample["id"]).one()
    assert version.version_number == 1
    assert version.change_type == "create"
    assert version.snapshot["verification_status"] == "Draft"


def test_approval_workflow_publishes_only_approved_samples(client, db, seed_data):
    field_token = login_token(client, "field_officer@example.com")
    reviewer_token = login_token(client, "reviewer@example.com")

    draft = create_sample(client, seed_data, field_token, sample_code="SAMPLE-APPROVAL")

    hidden_detail = client.get(f"/api/public/samples/{draft['id']}")
    assert hidden_detail.status_code == 404

    submitted_payload = sample_payload(seed_data, sample_code="SAMPLE-APPROVAL", status="Submitted")
    submitted_payload["remarks"] = "Ready for review"
    submitted = client.put(
        f"/api/staff/samples/{draft['id']}",
        json=submitted_payload,
        headers=auth_header(field_token),
    )
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["verification_status"] == "Pending"
    assert submitted.json()["public_visibility"] is False

    approved = client.post(
        f"/api/staff/samples/{draft['id']}/review",
        json={"decision": "Approved", "comments": "Approved for public release"},
        headers=auth_header(reviewer_token),
    )
    assert approved.status_code == 200, approved.text
    approved_sample = approved.json()
    assert approved_sample["status"] == "Approved"
    assert approved_sample["verification_status"] == "Approved"
    assert approved_sample["public_visibility"] is True

    public_list = client.get("/api/public/samples")
    assert public_list.status_code == 200
    assert any(item["id"] == draft["id"] for item in public_list.json())

    versions = (
        db.query(SampleVersion)
        .filter(SampleVersion.sample_id == draft["id"])
        .order_by(SampleVersion.version_number)
        .all()
    )
    assert [version.change_type for version in versions] == [
        "create",
        "status_update",
        "review_decision",
    ]


def test_sample_create_rejects_invalid_references_duplicate_codes_and_blank_attachments(client, seed_data):
    field_token = login_token(client, "field_officer@example.com")
    create_sample(client, seed_data, field_token, sample_code="SAMPLE-VALIDATION")

    duplicate = client.post(
        "/api/staff/samples",
        json=sample_payload(seed_data, sample_code="SAMPLE-VALIDATION"),
        headers=auth_header(field_token),
    )
    assert duplicate.status_code == 409

    invalid_type_payload = sample_payload(seed_data, sample_code="SAMPLE-BAD-TYPE")
    invalid_type_payload["sample_type_id"] = "00000000-0000-0000-0000-000000000000"
    invalid_type = client.post("/api/staff/samples", json=invalid_type_payload, headers=auth_header(field_token))
    assert invalid_type.status_code == 422

    blank_attachment_payload = sample_payload(seed_data, sample_code="SAMPLE-BAD-ATTACHMENT")
    blank_attachment_payload["attachments"][0]["file_name"] = ""
    blank_attachment = client.post("/api/staff/samples", json=blank_attachment_payload, headers=auth_header(field_token))
    assert blank_attachment.status_code == 422


def test_approved_and_rejected_samples_cannot_be_edited(client, seed_data):
    field_token = login_token(client, "field_officer@example.com")
    reviewer_token = login_token(client, "reviewer@example.com")

    for sample_code, decision in [("SAMPLE-LOCK-APPROVED", "Approved"), ("SAMPLE-LOCK-REJECTED", "Rejected")]:
        sample = create_sample(client, seed_data, field_token, sample_code=sample_code, status="Submitted")
        review = client.post(
            f"/api/staff/samples/{sample['id']}/review",
            json={"decision": decision, "comments": "Final decision"},
            headers=auth_header(reviewer_token),
        )
        assert review.status_code == 200, review.text

        update_payload = sample_payload(seed_data, sample_code=sample_code, status="Draft")
        update = client.put(f"/api/staff/samples/{sample['id']}", json=update_payload, headers=auth_header(field_token))
        assert update.status_code == 400


def test_rejected_and_correction_requested_samples_stay_private(client, seed_data):
    field_token = login_token(client, "field_officer@example.com")
    reviewer_token = login_token(client, "reviewer@example.com")
    decisions = [
        ("SAMPLE-REJECT", "Rejected", "Rejected", "Rejected"),
        ("SAMPLE-CORRECT", "Correction Requested", "Correction Requested", "Pending"),
    ]

    for sample_code, decision, expected_status, expected_verification in decisions:
        sample = create_sample(client, seed_data, field_token, sample_code=sample_code, status="Submitted")
        review = client.post(
            f"/api/staff/samples/{sample['id']}/review",
            json={"decision": decision, "comments": "Needs attention"},
            headers=auth_header(reviewer_token),
        )
        assert review.status_code == 200, review.text
        assert review.json()["status"] == expected_status
        assert review.json()["verification_status"] == expected_verification
        assert review.json()["public_visibility"] is False

        public_detail = client.get(f"/api/public/samples/{sample['id']}")
        assert public_detail.status_code == 404


def test_public_access_is_read_only(client, seed_data):
    public_write = client.post("/api/public/samples", json={})
    assert public_write.status_code == 405

    public_list = client.get("/api/public/samples")
    assert public_list.status_code == 200
    assert public_list.json() == []


def test_audit_logging_records_create_status_update_and_review(client, db, seed_data):
    field_token = login_token(client, "field_officer@example.com")
    reviewer_token = login_token(client, "reviewer@example.com")
    sample = create_sample(client, seed_data, field_token, sample_code="SAMPLE-AUDIT")

    update_payload = sample_payload(seed_data, sample_code="SAMPLE-AUDIT", status="Submitted")
    update_payload["remarks"] = "Submitted for audit trail"
    client.put(f"/api/staff/samples/{sample['id']}", json=update_payload, headers=auth_header(field_token))

    client.post(
        f"/api/staff/samples/{sample['id']}/review",
        json={"decision": "Approved", "comments": "Audit approved"},
        headers={**auth_header(reviewer_token), "X-Forwarded-For": "203.0.113.10"},
    )

    audit_entries = (
        db.query(AuditLog)
        .filter(AuditLog.record_id == sample["id"])
        .all()
    )
    entries_by_action = {entry.action: entry for entry in audit_entries}

    assert set(entries_by_action) == {"create", "status_update", "review_decision"}
    assert entries_by_action["status_update"].old_values["status"] == "Draft"
    assert entries_by_action["status_update"].new_values["status"] == "Submitted"
    assert entries_by_action["review_decision"].old_values["public_visibility"] is False
    assert entries_by_action["review_decision"].new_values["public_visibility"] is True
    assert entries_by_action["review_decision"].ip_address == "203.0.113.10"
