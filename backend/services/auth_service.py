import secrets
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from datetime import timedelta


def generate_tokens(user_id, role='user'):
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={'role': role},
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token(
        identity=str(user_id),
        expires_delta=timedelta(days=30)
    )
    return access_token, refresh_token


def decode_jwt_token(token):
    try:
        return decode_token(token)
    except Exception:
        return None


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_verification_token():
    return secrets.token_urlsafe(32)


def generate_reset_token():
    return secrets.token_urlsafe(32)
