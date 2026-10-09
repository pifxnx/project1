import hmac
import hashlib
import secrets


def generate_secret_key() -> str:
    return secrets.token_hex(32)


def sign_payload(secret_key: str, body: bytes) -> str:

    return hmac.new(secret_key.encode(), body, hashlib.sha256).hexdigest()


def verify_signature(secret_key: str, body: bytes, signature: str) -> bool:
    expected_signature = sign_payload(secret_key, body)
    return hmac.compare_digest(expected_signature, signature)
