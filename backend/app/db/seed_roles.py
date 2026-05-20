"""Compatibility wrapper for role seeding.

Use app.db.seed to seed roles, permissions, and the first admin user together.
"""

from app.db.seed import seed_database


if __name__ == "__main__":
    seed_database()
