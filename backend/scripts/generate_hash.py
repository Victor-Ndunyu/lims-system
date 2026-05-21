#!/usr/bin/env python3
"""Generate bcrypt hash for a password."""

import bcrypt

password = "Animalhealth123"
password_bytes = password.encode('utf-8')
password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode('utf-8')

print(f"Password: {password}")
print(f"Hash: {password_hash}")
