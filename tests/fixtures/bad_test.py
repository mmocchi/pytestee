"""Test fixture with quality issues."""


def test_no_assertions():
    """Test with no assertions - should be flagged."""
    username = "testuser"
    email = "test@example.com"
    user = create_user(username, email)
    print(f"Created user: {user.username}")


def test_too_many_assertions():
    """Test with too many assertions."""
    user = create_user("test", "test@example.com")
    assert user.username == "test"
    assert user.email == "test@example.com" 
    assert user.username is not None
    assert user.email is not None
    assert len(user.username) > 0
    assert "@" in user.email


def test_no_clear_pattern():
    """Test without clear AAA pattern."""
    user = create_user("test", "test@example.com")
    assert user.username == "test"
    another_user = create_user("test2", "test2@example.com")
    assert another_user.username == "test2"
    final_check = user.username != another_user.username
    assert final_check


def create_user(username, email):
    """Mock user creation function."""
    class User:
        def __init__(self, username, email):
            self.username = username
            self.email = email
    
    return User(username, email)