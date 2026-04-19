# src/api/endpoints/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from src.db import users_col
from src.config.settings import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = getattr(settings, "JWT_SECRET", None) or "CHANGE_ME_DEV_SECRET"
JWT_ALG = getattr(settings, "JWT_ALG", None) or "HS256"
JWT_EXPIRES_HOURS = getattr(settings, "JWT_EXPIRES_HOURS", None) or 24

BCRYPT_MAX_PASSWORD_BYTES = 72


class SignupRequest(BaseModel):
    firstName: str = Field(min_length=1, max_length=80)
    lastName: str = Field(min_length=1, max_length=80)
    email: EmailStr
    # Keep 128 if you want, but we still enforce 72 bytes at runtime.
    password: str = Field(min_length=8, max_length=128)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def _ensure_bcrypt_password_ok(p: str) -> None:
    if p is None:
        raise HTTPException(status_code=400, detail="Password is required")

    pw_bytes = p.encode("utf-8")
    if len(pw_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Password must be 72 bytes or fewer (bcrypt limitation).",
        )


def _hash_password(p: str) -> str:
    _ensure_bcrypt_password_ok(p)
    return pwd_context.hash(p)


def _verify_password(p: str, hashed: str) -> bool:
    try:
        _ensure_bcrypt_password_ok(p)
        return pwd_context.verify(p, hashed)
    except HTTPException:
        return False
    except Exception:
        return False


def _create_token(user_id: str, email: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=int(JWT_EXPIRES_HOURS))).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def _serialize_user(u: dict) -> dict:
    return {
        "id": str(u["_id"]),
        "firstName": u.get("firstName"),
        "lastName": u.get("lastName"),
        "name": f'{u.get("firstName","")} {u.get("lastName","")}'.strip(),
        "email": u.get("email"),
        "role": u.get("role", "recruiter"),
        "createdAt": u.get("createdAt"),
    }


@router.post("/signup")
def signup(body: SignupRequest):
    email = body.email.lower().strip()

    existing = users_col.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")

    _ensure_bcrypt_password_ok(body.password)

    doc = {
        "firstName": body.firstName.strip(),
        "lastName": body.lastName.strip(),
        "email": email,
        "passwordHash": _hash_password(body.password),
        "role": "recruiter",
        "createdAt": datetime.utcnow().isoformat(),
    }

    ins = users_col.insert_one(doc)
    user = users_col.find_one({"_id": ins.inserted_id})
    token = _create_token(str(ins.inserted_id), email)

    return {"token": token, "user": _serialize_user(user)}


@router.post("/signin")
def signin(body: SigninRequest):
    email = body.email.lower().strip()

    user = users_col.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not _verify_password(body.password, user.get("passwordHash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_token(str(user["_id"]), email)
    return {"token": token, "user": _serialize_user(user)}