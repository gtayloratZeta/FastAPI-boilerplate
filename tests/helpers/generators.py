import uuid as uuid_pkg

from sqlalchemy.orm import Session

from src.app import models
from src.app.core.security import get_password_hash
from tests.conftest import fake


def create_user(db: Session, is_super_user: bool = False) -> models.User:
    """
    Creates a new user instance with fake data, adds it to the database, commits
    the changes, refreshes the user instance, and returns the newly created user
    object.

    Args:
        db (Session): Used to interact with a database, specifically to add a new
            user model to the database and commit the changes.
        is_super_user (bool): Optional, defaulting to `False`. It is used to
            determine whether the newly created user should be a superuser.

    Returns:
        models.User: An instance of a user model, containing generated attributes
        such as name, username, email, hashed password, profile image URL, and a
        unique identifier, along with the specified superuser status.

    """
    _user = models.User(
        name=fake.name(),
        username=fake.user_name(),
        email=fake.email(),
        hashed_password=get_password_hash(fake.password()),
        profile_image_url=fake.image_url(),
        uuid=uuid_pkg.uuid4(),
        is_superuser=is_super_user,
    )

    db.add(_user)
    db.commit()
    db.refresh(_user)

    return _user

