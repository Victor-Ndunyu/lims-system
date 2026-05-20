"""Compatibility wrapper for admin seeding.

Use app.db.seed with FIRST_ADMIN_EMAIL and FIRST_ADMIN_PASSWORD instead.
"""

from app.db.seed import seed_database


if __name__ == "__main__":
    seed_database()
