import bcrypt

from app import db
from app.models import User, UserProfile
from shared.auth.jwt_utils import create_access_token


def register_user_service(email: str, username: str, password: str):
    existing = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        return False, "User with given email or username already exists"

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        email=email,
        username=username,
        password_hash=hashed.decode("utf-8"),
    )
    profile = UserProfile(user=user)

    db.session.add(user)
    db.session.add(profile)
    db.session.commit()

    return True, {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }


def login_user_service(identifier: str, password: str):
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()
    if not user:
        return False, "Invalid credentials"

    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return False, "Invalid credentials"

    token = create_access_token(user_id=user.id, email=user.email)

    return True, {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        },
    }

