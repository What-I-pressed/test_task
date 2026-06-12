import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from db import get_session
from entities import User as UserModel

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_secret() -> bytes:
    return os.getenv("AUTH_SECRET", "travel-planner-auth-secret").encode("utf-8")


def hash_password(password: str, salt: Optional[str] = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("utf-8"),
        120_000,
    ).hex()
    return f"{salt_value}${digest}"


def verify_password(password: str, stored_value: str) -> bool:
    salt, _ = stored_value.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), stored_value)


def create_access_token(user_id: int, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "iat": int(time.time()),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_part = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    signature = hmac.new(get_auth_secret(), payload_part.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_part}.{signature}"


def decode_access_token(token: str) -> dict:
    try:
        payload_part, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    expected_signature = hmac.new(
        get_auth_secret(),
        payload_part.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    padded = payload_part + "=" * (-len(payload_part) % 4)
    try:
        payload_bytes = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest, session=Depends(get_session)):
    existing_user = session.query(UserModel).filter(UserModel.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = UserModel(
        username=data.username,
        password_hash=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=AuthResponse)
def login_user(data: LoginRequest, session=Depends(get_session)):
    user = session.query(UserModel).filter(UserModel.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return AuthResponse(access_token=create_access_token(user.id, user.username))


def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session=Depends(get_session),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user = session.query(UserModel).filter(UserModel.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
