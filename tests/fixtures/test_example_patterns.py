"""Test fixtures containing good and bad examples for each rule."""
from typing import Union

# PTCM001: AAA Pattern Detected in Comments - Good Examples

def test_aaa_standard_pattern() -> None:
    """Good example: Standard AAA pattern with comments."""
    # Arrange
    name = "John Doe"
    email = "john@example.com"

    # Act
    user = User.create(name, email)

    # Assert
    assert user.name == name
    assert user.email == email


def test_aaa_combined_act_assert() -> None:
    """Good example: Combined Act & Assert comment."""
    # Arrange
    calculator = Calculator()

    # Act & Assert
    assert calculator.add(2, 3) == 5


# PTCM001: Bad Examples (should not trigger)

def test_without_comments() -> None:
    """Bad example: No pattern comments."""
    user = User("John")
    result = user.get_name()
    assert result == "John"


def test_mixed_pattern_terminology() -> None:
    """Bad example: Mixed pattern terminology."""
    # Given
    user = User("John")
    # Act
    result = user.get_name()
    # Then
    assert result == "John"


# PTCM002: GWT Pattern Detected in Comments - Good Examples

def test_gwt_standard_pattern() -> None:
    """Good example: Standard GWT pattern."""
    # Given
    user = User("john", "password123")
    auth_service = AuthService()

    # When
    is_authenticated = auth_service.authenticate(user.username, "password123")

    # Then
    assert is_authenticated is True


def test_gwt_combined_when_then() -> None:
    """Good example: Combined When & Then."""
    # Given
    validator = EmailValidator()

    # When & Then
    assert validator.is_valid("test@example.com") is True


# PTST001: Structural Pattern - Good Examples

def test_structural_three_sections() -> None:
    """Good example: Clear three-section structure."""
    customer = Customer("John")
    product = Product("Laptop", 1000)

    order = OrderService.create_order(customer, product)

    assert order.customer == customer  # type: ignore[attr-defined]
    assert order.total == 1000  # type: ignore[attr-defined]
    assert order.status == "pending"  # type: ignore[attr-defined]


def test_structural_two_sections() -> None:
    """Good example: Simple two-section structure."""
    calculator = Calculator()

    result = calculator.multiply(5, 4)

    assert result == 20


# PTST001: Bad Examples (no structural separation)

def test_no_structural_separation() -> None:
    """Bad example: No structural separation."""
    user = User("John")
    assert user.get_name() == "John"


def test_mixed_code_no_sections() -> None:
    """Bad example: Mixed code without clear sections."""
    assert User("John").get_name() == "John"
    assert User("Jane").get_name() == "Jane"


# PTAS001: Too Few Assertions - Good Examples

def test_sufficient_assertions() -> None:
    """Good example: Has sufficient assertions."""
    user = User("John", "john@example.com")

    assert user.name == "John"
    assert user.email == "john@example.com"


def test_single_meaningful_assertion() -> None:
    """Good example: Single meaningful assertion."""
    result = Calculator().add(2, 3)
    assert result == 5


# PTAS001: Bad Examples (would trigger this rule)

def test_no_assertions() -> None:
    """Bad example: No assertions at all."""
    user = User("John")
    user.save()
    # Missing assertions to verify behavior!


def test_side_effects_only() -> None:
    """Bad example: Only side effects, no verification."""
    logger = Logger()
    logger.info("Test message")
    # Should assert log was written, state changed, etc.


# PTAS002: Too Many Assertions - Good Examples

def test_focused_user_validation() -> None:
    """Good example: Focused test with appropriate assertions."""
    user = User("John", "john@example.com", "password123")

    assert user.email == "john@example.com"
    assert user.is_valid() is True
    assert user.password_hash is not None


# PTAS002: Bad Examples (would trigger this rule)

def test_too_many_assertions() -> None:
    """Bad example: Too many assertions in single test."""
    user = User("John", "john@example.com", "password123")
    assert user.name == "John"
    assert user.email == "john@example.com"
    assert user.password_hash is not None
    assert user.is_valid() is True
    assert user.created_at is not None  # Too many!
    assert user.updated_at is not None
    assert user.is_active is True


# PTAS003: High Assertion Density - Good Examples

def test_high_density_focused() -> None:
    """Good example: High density but well-focused."""
    result = get_user()
    assert result.name == "John"  # type: ignore[attr-defined]
    assert result.age == 30  # type: ignore[attr-defined]
    assert result.active is True  # type: ignore[attr-defined]


# PTAS004: No Assertions - Bad Examples (would trigger this rule)

def test_completely_empty() -> None:
    """Bad example: No assertions found."""
    user = create_user("test")
    user.save()


# PTAS005: Assertion Count OK - Good Examples

def test_appropriate_assertion_count() -> None:
    """Good example: Appropriate assertion count."""
    result = process("test")
    assert result == "expected"


# Mock classes for examples
class User:
    """Mock User class for testing."""

    def __init__(self, name_or_email: str, email_or_password: Union[str, None] = None, password: Union[str, None] = None) -> None:
        self.name: str = name_or_email
        self.username: str = name_or_email
        self.email: Union[str, None] = None
        self.password: Union[str, None] = None

        if password is not None:
            # Three parameter case: User(name, email, password)
            self.email = email_or_password
            self.password = password
        elif email_or_password is not None and "@" in email_or_password:
            # Two parameter case with email: User(name, email)
            self.email = email_or_password
        elif email_or_password is not None:
            # Two parameter case: User(username, password)
            self.password = email_or_password

        self.password_hash: Union[str, None] = "hashed" if self.password else None
        self.created_at: str = "2023-01-01"
        self.updated_at: str = "2023-01-01"
        self.is_active: bool = True

    @classmethod
    def create(cls, name: str, email: str) -> 'User':
        """Create user with name and email."""
        return cls(name, email)

    def get_name(self) -> str:
        """Get user name."""
        return self.name

    def save(self) -> None:
        """Save user."""
        pass

    def is_valid(self) -> bool:
        """Check if user is valid."""
        return self.email is not None

    def is_password_strong(self) -> bool:
        """Check if password is strong."""
        return len(self.password or "") > 8


class Calculator:
    """Mock Calculator class for testing."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b


class AuthService:
    """Mock AuthService class for testing."""

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user."""
        return password == "password123"  # noqa: S105


class EmailValidator:
    """Mock EmailValidator class for testing."""

    def is_valid(self, email: str) -> bool:
        """Validate email."""
        return "@" in email


class Customer:
    """Mock Customer class for testing."""

    def __init__(self, name: str) -> None:
        self.name = name


class Product:
    """Mock Product class for testing."""

    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price


class OrderService:
    """Mock OrderService class for testing."""

    @staticmethod
    def create_order(customer: Customer, product: Product) -> object:
        """Create order."""
        return type('Order', (), {
            'customer': customer,
            'total': product.price,
            'status': 'pending'
        })()


class Logger:
    """Mock Logger class for testing."""

    def info(self, message: str) -> None:
        """Log info message."""
        pass


def get_user() -> object:
    """Get mock user object."""
    return type('User', (), {
        'name': 'John',
        'age': 30,
        'active': True
    })()


def create_user(name: str) -> User:
    """Create user with name."""
    return User(name)


def process(_data: object) -> str:
    """Process data."""
    return "expected"
