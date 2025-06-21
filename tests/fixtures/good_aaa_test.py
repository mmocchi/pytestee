"""Test fixture with good AAA pattern."""
from typing import Any


def test_user_creation_with_aaa_comments() -> None:
    """Test creating a user with proper AAA pattern using comments."""
    # Arrange
    username = "testuser"
    email = "test@example.com"

    # Act
    user = create_user(username, email)

    # Assert
    assert user.username == username
    assert user.email == email


def test_user_creation_with_structural_separation() -> None:
    """Test creating a user with structural AAA pattern."""
    username = "testuser"
    email = "test@example.com"

    user = create_user(username, email)

    assert user.username == username
    assert user.email == email


def create_user(username: str, email: str) -> Any:
    """Mock user creation function."""
    class User:
        def __init__(self, username: str, email: str) -> None:
            self.username = username
            self.email = email

    return User(username, email)
