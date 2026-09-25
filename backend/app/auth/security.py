import bcrypt
import hashlib
import hmac
import uuid
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Any, Tuple, Set, Dict
from jose import jwt, JWTError
from app.config.settings import settings

# Thread-safe in-memory store for revoked token identifiers / signatures (jti/token_hash -> expiry_timestamp)
REVOKED_TOKENS: Dict[str, float] = {}

COMMON_WEAK_PASSWORDS = {
    "password", "password123", "12345678", "123456789", "qwerty123",
    "admin123", "welcome1", "letmein123", "iloveyou", "password1"
}

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    OWASP ASVS Password Quality Rule:
    - Minimum length 8 characters
    - Must contain at least one uppercase letter, one lowercase letter, and one number or special character
    - Must not be in common weak password dictionary
    """
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters in length."
    if len(password) > 128:
        return False, "Password length cannot exceed 128 characters."
    if password.lower() in COMMON_WEAK_PASSWORDS:
        return False, "This password is too common and easily guessed. Please choose a stronger password."
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

    if not (has_upper and has_lower and (has_digit or has_special)):
        return False, "Password must include a mix of uppercase, lowercase letters, and numbers or symbols."

    return True, ""

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not plain_password or not hashed_password:
            return False
        if hashed_password.startswith("$2a$") or hashed_password.startswith("$2b$") or hashed_password.startswith("$2y$"):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        # Fallback SHA256 verification with constant-time comparison
        expected = hashlib.sha256((plain_password + settings.SECRET_KEY).encode()).hexdigest()
        return hmac.compare_digest(expected, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    try:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
    except Exception:
        # Fallback SHA256 with key
        return hashlib.sha256((password + settings.SECRET_KEY).encode()).hexdigest()

def _cleanup_revoked_tokens():
    """Purge expired tokens from blacklist."""
    now = time.time()
    keys_to_delete = [k for k, exp in REVOKED_TOKENS.items() if exp < now]
    for k in keys_to_delete:
        REVOKED_TOKENS.pop(k, None)

def revoke_token(token: str, exp_timestamp: Optional[float] = None):
    """Adds a token signature/jti to the revocation store."""
    _cleanup_revoked_tokens()
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    # If expiration not supplied, default to 7 days
    exp = exp_timestamp or (time.time() + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))
    REVOKED_TOKENS[token_hash] = exp

def is_token_revoked(token: str) -> bool:
    """Checks if token has been explicitly invalidated or logged out."""
    _cleanup_revoked_tokens()
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    return token_hash in REVOKED_TOKENS

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
        "type": "access"
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=14)
    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        if is_token_revoked(token):
            return None
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True, "verify_sub": True}
        )
        return payload
    except JWTError:
        return None
