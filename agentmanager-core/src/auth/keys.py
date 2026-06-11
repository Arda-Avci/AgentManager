from __future__ import annotations

import hashlib
import hmac
import secrets
from base64 import b64decode, b64encode

from cryptography.fernet import Fernet

from src.config import settings


def _get_fernet() -> Fernet:
    key = settings.master_key
    if len(key.encode()) < 32:
        key = key.ljust(32, "x")[:32]
    fernet_key = b64encode(key.encode().ljust(32, b"\0")[:32])
    return Fernet(fernet_key)


def generate_api_key() -> str:
    return f"am_{secrets.token_urlsafe(32)}"


def hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_key(api_key: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_key(api_key), stored_hash)


def encrypt_api_key(api_key: str) -> str:
    f = _get_fernet()
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted_key.encode()).decode()
