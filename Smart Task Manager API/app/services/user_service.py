from io import StringIO
from fastapi import UploadFile
import csv
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, hash_password


def authenticate_user(database: Session, email: str, password: str):
    user = database.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return user


def create_user(
        database: Session,
        email: str,
        password: str,
        is_active: bool = True,
        is_superuser: bool = False,
        is_verified: bool = False
):
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified
    )
    database.add(user)
    database.commit()
    database.refresh(user)
    return user


def import_users(
        database: Session,
        file: UploadFile
):
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(contents))

    users = []

    for row in reader:
        users.append(
            User(
                email=row["email"],
                hashed_password=hash_password(row["password"]),
                is_active=str(row["is_active"]).strip().lower() in [
                    "true", "1", "yes"
                ],
                is_superuser=str(row["is_superuser"]).strip().lower() in [
                    "true", "1", "yes"
                ],
                is_verified=str(row["is_verified"]).strip().lower() in [
                    "true", "1", "yes"
                ]
            )
        )

    database.bulk_save_objects(users)
    database.commit()

    return {
        "message": "Users imported successfully"
    }
