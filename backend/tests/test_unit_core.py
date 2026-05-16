from datetime import datetime, timezone

from app.core.audit import log_audit, make_sample_snapshot, record_sample_version
from app.core.security import (
    create_session_token,
    create_user_session,
    get_user_session_by_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.models.sample import Sample


def test_password_hashing_and_verification_round_trip():
    password_hash = hash_password("correct-password")

    assert password_hash != "correct-password"
    assert verify_password("correct-password", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_session_tokens_are_hashed_and_retrievable(db, seed_data):
    user = seed_data["users"]["field_officer"]
    token, session = create_user_session(db, user, device_info="unit-test")

    assert token != session.token_hash
    assert session.token_hash == hash_session_token(token)
    assert get_user_session_by_token(db, token).id == session.id
    assert get_user_session_by_token(db, create_session_token()) is None


def test_sample_snapshot_serializes_core_fields(seed_data):
    sample = Sample(
        sample_code="UNIT-SNAPSHOT",
        sample_type_id=seed_data["sample_type"].id,
        collection_date=datetime(2026, 5, 11, tzinfo=timezone.utc),
        collector_id=seed_data["users"]["field_officer"].id,
        location_id=seed_data["location"].id,
        status="Draft",
        verification_status="Draft",
        public_visibility=False,
        description="Snapshot description",
        remarks="Snapshot remarks",
    )

    snapshot = make_sample_snapshot(sample)

    assert snapshot["sample_code"] == "UNIT-SNAPSHOT"
    assert snapshot["collection_date"] == "2026-05-11T00:00:00+00:00"
    assert snapshot["collector_id"] == str(seed_data["users"]["field_officer"].id)
    assert snapshot["attachments"] == []


def test_record_sample_version_increments_versions(db, seed_data):
    sample = Sample(
        sample_code="UNIT-VERSION",
        sample_type_id=seed_data["sample_type"].id,
        collection_date=datetime(2026, 5, 11, tzinfo=timezone.utc),
        collector_id=seed_data["users"]["field_officer"].id,
        location_id=seed_data["location"].id,
        status="Draft",
        verification_status="Draft",
        public_visibility=False,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)

    first = record_sample_version(db, sample, "create", str(seed_data["users"]["field_officer"].id))
    sample.status = "Submitted"
    sample.verification_status = "Pending"
    db.commit()
    second = record_sample_version(db, sample, "status_update", str(seed_data["users"]["field_officer"].id))

    assert first.version_number == 1
    assert second.version_number == 2
    assert second.snapshot["status"] == "Submitted"


def test_log_audit_persists_old_and_new_values(db, seed_data):
    entry = log_audit(
        db=db,
        table_name="samples",
        record_id="00000000-0000-0000-0000-000000000001",
        action="status_update",
        old_values={"status": "Draft"},
        new_values={"status": "Submitted"},
        performed_by=str(seed_data["users"]["field_officer"].id),
        ip_address="127.0.0.1",
    )

    assert entry.table_name == "samples"
    assert entry.action == "status_update"
    assert entry.old_values == {"status": "Draft"}
    assert entry.new_values == {"status": "Submitted"}
    assert entry.ip_address == "127.0.0.1"
