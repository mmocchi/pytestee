"""Test fixture for Japanese naming rule testing."""


def test_日本語メソッド名() -> None:
    """日本語でのテストメソッド名の例。"""
    # Arrange
    value = 1

    # Act
    result = value + 1

    # Assert
    assert result == 2


def test_ひらがなでのテスト() -> None:
    """ひらがなを使ったテストメソッド名。"""
    text = "テスト"
    assert len(text) > 0


def test_カタカナでのテスト() -> None:
    """カタカナを使ったテストメソッド名。"""
    data = {"key": "value"}
    assert "key" in data


def test_漢字を含むテスト() -> None:
    """漢字を含むテストメソッド名。"""
    number = 42
    assert number > 0


def test_mixed_japanese_englishテスト() -> None:
    """Mixed Japanese and English test method name."""
    result = True
    assert result is True


def test_english_only_method() -> None:
    """English only test method name."""
    count = 5
    assert count == 5


def helper_method() -> str:
    """Non-test helper method should be ignored."""
    return "helper"
