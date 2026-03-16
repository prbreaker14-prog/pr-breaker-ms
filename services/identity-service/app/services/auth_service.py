import bcrypt
import hashlib
import os
import random
from datetime import datetime, timedelta

from app import db
from app.models import User, UserProfile, RefreshToken, PasswordResetOTP
from shared.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_token,
)

from app.services.email_service import send_email


def register_user_service(
    user_email: str,
    user_name: str,
    user_password: str,
    age: int | None = None,
    gender: str | None = None,
    height: float | None = None,
    weight: float | None = None,
):
    existing = User.query.filter(
        (User.email == user_email) | (User.username == user_name)
    ).first()
    if existing:
        return False, "User with given email or username already exists"

    hashed = bcrypt.hashpw(user_password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        email=user_email,
        username=user_name,
        password_hash=hashed.decode("utf-8"),
    )
    profile = UserProfile(
        user=user,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
    )

    db.session.add(user)
    db.session.add(profile)
    db.session.commit()

    return True, {
        "userId": user.id,
        "userEmail": user.email,
        "userName": user.username,
        "profile": {
            "age": profile.age,
            "gender": profile.gender,
            "height": profile.height,
            "weight": profile.weight,
        },
    }


def login_user_service(
    user_email: str | None = None, user_name: str | None = None, password: str = ""
):
    # Accept either email or username for login
    identifier_filter = []
    if user_email:
        identifier_filter.append(User.email == user_email)
    if user_name:
        identifier_filter.append(User.username == user_name)

    if not identifier_filter:
        return False, "Invalid credentials"

    user = User.query.filter(*identifier_filter).first()
    if not user:
        return False, "Invalid credentials"

    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return False, "Invalid credentials"

    access_token = create_access_token(user_id=user.id, email=user.email)
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)

    _store_refresh_token(user_id=user.id, refresh_token=refresh_token)

    return True, {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "userId": user.id,
            "userEmail": user.email,
            "userName": user.username,
        },
    }


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _store_refresh_token(user_id: str, refresh_token: str) -> None:
    ok, payload, _err = decode_token(refresh_token)
    if not ok or not payload:
        return
    exp_ts = payload.get("exp")
    # PyJWT returns exp as int timestamp
    expires_at = datetime.utcfromtimestamp(exp_ts) if isinstance(exp_ts, (int, float)) else datetime.utcnow() + timedelta(days=30)

    rt = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(refresh_token),
        expires_at=expires_at,
    )
    db.session.add(rt)
    db.session.commit()


def refresh_token_service(refresh_token: str):
    ok, payload, error = decode_token(refresh_token)
    if not ok or not payload:
        return False, error or "Invalid token"

    if payload.get("type") != "refresh":
        return False, "Invalid token type"

    token_hash = _hash_token(refresh_token)
    rt = RefreshToken.query.filter_by(token_hash=token_hash).first()
    if not rt or rt.revoked_at is not None:
        return False, "Refresh token revoked or not found"

    # Rotate: revoke old and issue new
    rt.revoked_at = datetime.utcnow()

    user = User.query.get(payload.get("user_id"))
    if not user:
        db.session.commit()
        return False, "User not found"

    new_access = create_access_token(user_id=user.id, email=user.email)
    new_refresh = create_refresh_token(user_id=user.id, email=user.email)
    db.session.commit()

    _store_refresh_token(user_id=user.id, refresh_token=new_refresh)

    return True, {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


def forgot_password_service(email: str):
    """
    Always respond success-ish to avoid leaking whether an email exists.
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return True, {"sent": True}

    otp = f"{random.randint(0, 999999):06d}"
    otp_hash = bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    record = PasswordResetOTP(
        user_id=user.id,
        email=user.email,
        otp_hash=otp_hash,
        expires_at=expires_at,
    )
    db.session.add(record)
    db.session.commit()

    subject = "Your password reset OTP"
    body = f"Your OTP is: {otp}\n\nIt expires in 10 minutes."
    sent = send_email(user.email, subject, body)

    dev_show = os.getenv("DEV_SHOW_OTP", "false").lower() in ("1", "true", "yes")
    data = {"sent": bool(sent)}
    if dev_show:
        data["otp_dev"] = otp
    return True, data


def verify_reset_otp_service(email: str, otp: str):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "Invalid OTP"

    record = (
        PasswordResetOTP.query.filter_by(user_id=user.id, email=email, consumed_at=None)
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )
    if not record:
        return False, "Invalid OTP"
    if record.expires_at < datetime.utcnow():
        return False, "OTP expired"

    if not bcrypt.checkpw(otp.encode("utf-8"), record.otp_hash.encode("utf-8")):
        return False, "Invalid OTP"

    record.consumed_at = datetime.utcnow()
    db.session.commit()

    reset_token = create_password_reset_token(user_id=user.id, email=user.email)
    return True, {"reset_token": reset_token}


def reset_password_service(reset_token: str, new_password: str):
    ok, payload, error = decode_token(reset_token)
    if not ok or not payload:
        return False, error or "Invalid token"

    if payload.get("type") != "reset":
        return False, "Invalid token type"

    user = User.query.get(payload.get("user_id"))
    if not user or user.email != payload.get("email"):
        return False, "Invalid token"

    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user.password_hash = hashed

    # Revoke all refresh tokens for this user (forces re-login everywhere)
    RefreshToken.query.filter_by(user_id=user.id, revoked_at=None).update(
        {"revoked_at": datetime.utcnow()}
    )

    db.session.commit()
    return True, {"password_reset": True}

