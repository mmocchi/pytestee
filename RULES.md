# Pytestee Rule Reference

このドキュメントでは、pytesteeで実装されているすべてのルールについて、識別と設定を容易にするカテゴリ化されたルールIDシステムと共に説明します。

## Rule Categories

### PTCM: Comment-Based Pattern Rules

#### PTCM001: AAA Pattern Detected in Comments
- **Default Severity**: ERROR (configurable)
- **Description**: コメント解析によってAAA（Arrange, Act, Assert）パターンが検出された場合
- **Good Examples**:
  ```python
  # Example 1: Standard AAA pattern
  def test_user_creation():
      # Arrange
      name = "John Doe"
      email = "john@example.com"
      
      # Act
      user = User.create(name, email)
      
      # Assert
      assert user.name == name
      assert user.email == email
  
  # Example 2: Combined Act & Assert comment
  def test_simple_calculation():
      # Arrange
      calculator = Calculator()
      
      # Act & Assert
      assert calculator.add(2, 3) == 5
  ```
- **Bad Examples** (would not trigger this rule):
  ```python
  # Bad: No pattern comments
  def test_without_comments():
      user = User("John")
      result = user.get_name()
      assert result == "John"
  
  # Bad: Mixed pattern terminology
  def test_mixed_patterns():
      # Given
      user = User("John")
      # Act
      result = user.get_name()
      # Then
      assert result == "John"
  ```

#### PTCM002: GWT Pattern Detected in Comments  
- **Default Severity**: ERROR (configurable)
- **Description**: コメント解析によってGWT（Given, When, Then）パターンが検出された場合
- **Good Examples**:
  ```python
  # Example 1: Standard GWT pattern
  def test_user_authentication():
      # Given
      user = User("john", "password123")
      auth_service = AuthService()
      
      # When
      is_authenticated = auth_service.authenticate(user.username, "password123")
      
      # Then
      assert is_authenticated is True
  
  # Example 2: Combined When & Then
  def test_quick_validation():
      # Given
      validator = EmailValidator()
      
      # When & Then
      assert validator.is_valid("test@example.com") is True
  ```
- **Bad Examples** (would not trigger this rule):
  ```python
  # Bad: No pattern comments
  def test_without_comments():
      user = User("John")
      result = user.get_name()
      assert result == "John"
  
  # Bad: Mixed with AAA terminology
  def test_mixed_patterns():
      # Arrange
      user = User("John")
      # When
      result = user.get_name()
      # Assert
      assert result == "John"
  ```

### PTST: Structural Pattern Rules

#### PTST001: AAA Pattern Detected Through Structural Separation
- **Default Severity**: ERROR (configurable)
- **Description**: コードセクションを分離する空行によってAAAパターンが検出された場合
- **Good Examples**:
  ```python
  # Example 1: Clear three-section structure
  def test_order_processing():
      # Arrange section
      customer = Customer("John")
      product = Product("Laptop", 1000)
      
      # Act section
      order = OrderService.create_order(customer, product)
      
      # Assert section
      assert order.customer == customer
      assert order.total == 1000
      assert order.status == "pending"
  
  # Example 2: Simple two-section structure
  def test_calculation():
      calculator = Calculator()
      
      result = calculator.multiply(5, 4)
      
      assert result == 20
  ```
- **Bad Examples** (would not trigger this rule):
  ```python
  # Bad: No structural separation
  def test_no_separation():
      user = User("John")
      result = user.get_name()
      assert result == "John"
  
  # Bad: Mixed code without clear sections
  def test_mixed_code():
      user = User("John")
      other_user = User("Jane")
      result1 = user.get_name()
      assert result1 == "John"
      result2 = other_user.get_name()
      assert result2 == "Jane"
  ```

#### PTST002: AAA/GWT Pattern Not Clearly Detected
- **Default Severity**: ERROR (configurable)
- **Description**: 明確なパターン構造が見つからない場合、テスト構成の改善を検討してください
- **修正方法**: コメント、空行を追加するか、テストロジックを再構築してください
- **Example**:
  ```python
  # Bad - no clear structure
  def test_example():
      data = "test"
      result = process(data)
      assert result == expected
      more_data = "test2"
      result2 = process(more_data)
      assert result2 == expected2
  ```

### PTLG: Logical Pattern Rules

#### PTLG001: AAA Pattern Detected Through Code Flow Analysis
- **Default Severity**: ERROR (configurable)
- **Description**: コード構造のAST解析によってAAAパターンが検出された場合
- **良い例**: コードが自然にarrange → act → assertの流れに従っている場合
- **Example**:
  ```python
  def test_example():
      data = "test"        # Arrange (assignments)
      result = process(data)  # Act (function calls)
      assert result == expected  # Assert (assertions)
  ```

### PTNM: Naming Rules

#### PTNM001: Japanese Characters in Test Method Names
- **Default Severity**: ERROR (configurable) 
- **Description**: テストメソッド名に日本語文字が含まれているかどうかをチェック
- **Good Examples**:
  ```python
  # Good: Japanese characters used for readability
  def test_日本語メソッド名():
      """日本語でのテストメソッド名の例。"""
      # Test implementation
      assert True
  
  def test_ユーザー作成():
      """ユーザー作成機能のテスト。"""
      # Test implementation
      assert True
  ```
- **Warning Examples** (would suggest using Japanese):
  ```python
  # Warning: English-only method name
  def test_user_creation():
      """Could be more readable with Japanese."""
      # Test implementation
      assert True
  ```

### PTVL: Vulnerability Detection Rules

#### PTVL001: Private Attribute/Method Access Detection
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数がプライベート属性やメソッド（アンダースコアで始まる）にアクセスしている場合
- **Good Examples**:
  ```python
  # Good: Using public interfaces
  def test_user():
      user = User("Alice")
      assert user.get_name() == "Alice"
      assert user.is_valid()
  
  # Good: Using public properties
  def test_user_properties():
      user = User("Alice")
      assert user.name == "Alice"
      assert user.email is not None
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Accessing private attribute
  def test_user():
      user = User("Alice")
      assert user._internal_id is not None  # Private attribute access
      assert user.name == "Alice"
  
  # Bad: Calling private method
  def test_user_hash():
      user = User("Alice")
      hash_value = user._calculate_hash()  # Private method call
      assert hash_value == "abc"
  ```

#### PTVL002: Time Dependency Detection
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数が時間に依存するコード（`datetime.now()`, `time.time()`など）を含んでいる場合
- **Good Examples**:
  ```python
  # Good: Using fixed time values
  def test_timestamp():
      fixed_time = datetime(2023, 1, 1, 12, 0, 0)
      result = process_time(fixed_time)
      assert result is not None
  
  # Good: Using mocks
  @patch('module.datetime')
  def test_timestamp(mock_datetime):
      mock_datetime.now.return_value = datetime(2023, 1, 1)
      result = get_current_time()
      assert result == datetime(2023, 1, 1)
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Direct use of datetime.now()
  def test_timestamp():
      current_time = datetime.now()  # Time dependency
      result = process_time(current_time)
      assert result is not None
  
  # Bad: Using time.time() directly
  def test_timing():
      start = time.time()  # Time dependency
      process_something()
      end = time.time()    # Time dependency
      assert end > start
  ```

#### PTVL003: Random Dependency Detection
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数がランダム性に依存するコード（`random()`関数など）を含んでいる場合
- **Good Examples**:
  ```python
  # Good: Using fixed seed
  @patch('module.random.randint')
  def test_random_id(mock_random):
      mock_random.return_value = 12345678
      user_id = generate_user_id()
      assert user_id == "12345678"
  
  # Good: Using deterministic values
  def test_user_id_format():
      user_id = generate_user_id_with_seed(42)
      assert len(user_id) == 8
      assert user_id.isdigit()
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Using random values directly
  def test_random_id():
      user_id = random.randint(10000000, 99999999)  # Random dependency
      assert len(str(user_id)) == 8
  
  # Bad: Using uuid4 without control
  def test_unique_id():
      unique_id = uuid.uuid4()  # Random dependency
      assert unique_id is not None
  ```

#### PTVL004: Global State Modification Detection
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数がグローバル変数を変更している場合
- **Good Examples**:
  ```python
  # Good: Using dependency injection
  def test_config(mock_config):
      service = Service(config=mock_config)
      result = service.process()
      assert result is not None
  
  # Good: Using context managers
  def test_settings():
      with patch.object(settings, 'DEBUG', True):
          result = debug_function()
          assert result is True
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Modifying global variables
  def test_global_config():
      global CONFIG
      CONFIG = {"debug": True}  # Global state modification
      result = process_with_config()
      assert result is not None
  
  # Bad: Module-level variable modification
  def test_module_settings():
      settings.DEBUG = True  # Module state modification
      result = debug_process()
      assert result is not None
  ```

#### PTVL005: Class Variable Manipulation Detection
- **Default Severity**: ERROR (configurable)
- **Description**: テストクラス内でクラス変数を操作している場合
- **Good Examples**:
  ```python
  # Good: Using instance variables
  class TestUserService:
      def test_user_creation(self):
          self.service = UserService()
          user = self.service.create_user("Alice")
          assert user.name == "Alice"
  
  # Good: Using fixtures
  class TestCounter:
      def test_increment(self):
          counter = Counter(initial=0)
          counter.increment()
          assert counter.value == 1
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Modifying class variables
  class TestCounter:
      counter = 0  # Class variable
      
      def test_increment(self):
          TestCounter.counter += 1  # Class variable modification
          assert TestCounter.counter == 1  # Test execution order dependent
  ```

### PTEC: Edge Case Coverage Rules

#### PTEC001: Numeric Edge Cases Missing
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数が数値のエッジケース（0、負数、最大最小値、オーバーフロー）をカバーしていない場合
- **設定**: `min_numeric_edge_cases`（デフォルト: 1）
- **Good Examples**:
  ```python
  # Good: Covers numeric edge cases
  @pytest.mark.parametrize("value", [0, -1, 1, 999999, -999999])
  def test_numeric_validation(value):
      result = validate_number(value)
      assert result is not None
  
  # Good: Testing zero and negative cases
  def test_calculation_edge_cases():
      calculator = Calculator()
      
      # Test zero
      assert calculator.divide(10, 1) == 10
      assert calculator.divide(0, 1) == 0
      
      # Test negative numbers
      assert calculator.multiply(-5, 3) == -15
      assert calculator.multiply(-2, -4) == 8
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Only tests positive normal values
  def test_calculation():
      calculator = Calculator()
      assert calculator.add(2, 3) == 5
      assert calculator.multiply(4, 5) == 20
      # Missing: zero, negative, boundary values
  
  # Bad: No edge case coverage for numeric operations
  def test_price_calculation():
      price = calculate_price(quantity=5, unit_price=10.0)
      assert price == 50.0
      # Missing: quantity=0, negative values, very large numbers
  ```

#### PTEC002: Collection Edge Cases Missing
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数がコレクション（リスト、辞書など）のエッジケース（空、単一要素、大きなサイズ）をカバーしていない場合
- **設定**: `min_collection_edge_cases`（デフォルト: 1）
- **Good Examples**:
  ```python
  # Good: Tests empty, single, and multiple element cases
  @pytest.mark.parametrize("items", [[], [1], [1, 2, 3, 4, 5]])
  def test_list_processing(items):
      result = process_list(items)
      assert isinstance(result, list)
  
  # Good: Explicit edge case testing
  def test_user_list_operations():
      user_service = UserService()
      
      # Empty list
      empty_result = user_service.get_users([])
      assert empty_result == []
      
      # Single user
      single_result = user_service.get_users([1])
      assert len(single_result) == 1
      
      # Multiple users
      multi_result = user_service.get_users([1, 2, 3])
      assert len(multi_result) == 3
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Only tests with normal-sized collections
  def test_user_processing():
      users = [User("Alice"), User("Bob"), User("Charlie")]
      result = process_users(users)
      assert len(result) == 3
      # Missing: empty list, single user cases
  
  # Bad: No consideration of collection size variations
  def test_data_aggregation():
      data = {"key1": "value1", "key2": "value2"}
      result = aggregate_data(data)
      assert result is not None
      # Missing: empty dict, single key, very large dict
  ```

#### PTEC003: String Edge Cases Missing
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数が文字列のエッジケース（None、空文字、特殊文字、長い文字列）をカバーしていない場合
- **設定**: `min_string_edge_cases`（デフォルト: 1）
- **Good Examples**:
  ```python
  # Good: Comprehensive string edge case testing
  @pytest.mark.parametrize("text", [
      None, "", "a", "normal text", 
      "text\nwith\nnewlines", "日本語テキスト", "x" * 1000
  ])
  def test_text_processing(text):
      result = process_text(text)
      # Each case handled appropriately
      if text is None:
          assert result is None
      elif text == "":
          assert result == ""
      else:
          assert len(result) > 0
  
  # Good: Explicit string edge cases
  def test_email_validation():
      validator = EmailValidator()
      
      # None and empty
      assert validator.is_valid(None) is False
      assert validator.is_valid("") is False
      
      # Special characters
      assert validator.is_valid("test@example.com") is True
      assert validator.is_valid("user+tag@domain.co.jp") is True
      
      # Very long email
      long_email = "a" * 200 + "@example.com"
      assert validator.is_valid(long_email) is False
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Only tests normal string cases
  def test_name_formatting():
      formatter = NameFormatter()
      result = formatter.format("John Doe")
      assert result == "John Doe"
      # Missing: None, empty string, special characters
  
  # Bad: No consideration of string edge cases
  def test_message_processing():
      message = "Hello, World!"
      result = process_message(message)
      assert "Hello" in result
      # Missing: empty message, None, very long message, special chars
  ```

#### PTEC004: Normal/Abnormal Test Ratio Warning
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数の正常ケースと異常ケースの比率が推奨される7:3比率から大きく逸脱している場合
- **設定**: `normal_ratio_target`（デフォルト: 0.7）、`abnormal_ratio_target`（デフォルト: 0.3）
- **Good Examples**:
  ```python
  # Good: Balanced normal/abnormal case ratio
  @pytest.mark.parametrize("input_data,expected", [
      # Normal cases (70%)
      ("valid@email.com", True),
      ("user@domain.org", True),
      ("test123@example.net", True),
      ("name+tag@site.com", True),
      ("user@subdomain.example.com", True),
      ("simple@test.co", True),
      ("long.name@example-site.com", True),
      # Abnormal cases (30%)
      ("invalid-email", False),
      ("@missing-local.com", False),
      ("missing-at-sign.com", False),
  ])
  def test_email_validation_comprehensive(input_data, expected):
      result = validate_email(input_data)
      assert result == expected
  ```
- **Warning Examples** (would trigger this rule):
  ```python
  # Warning: Too many normal cases, not enough edge/error cases
  @pytest.mark.parametrize("value", [
      1, 2, 3, 4, 5, 6, 7, 8, 9, 10  # All normal cases, no edge cases
  ])
  def test_number_processing(value):
      result = process_number(value)
      assert result > 0
  
  # Warning: Too many abnormal cases, not enough normal cases  
  @pytest.mark.parametrize("invalid_input", [
      None, "", "invalid", -1, 0, [], {}, False
  ])
  def test_validation_errors_only(invalid_input):
      with pytest.raises(ValueError):
          validate_input(invalid_input)
  ```

#### PTEC005: Overall Edge Case Coverage Score
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数の全体的なエッジケース網羅性スコアが低い場合（数値、コレクション、文字列の各カテゴリを総合評価）
- **設定**: `min_coverage_score`（デフォルト: 0.6）
- **Good Examples**:
  ```python
  # Good: High edge case coverage across multiple types
  def test_user_data_processing():
      processor = UserDataProcessor()
      
      # Numeric edge cases
      assert processor.validate_age(0) is False
      assert processor.validate_age(-1) is False
      assert processor.validate_age(150) is False
      assert processor.validate_age(25) is True
      
      # String edge cases  
      assert processor.validate_name(None) is False
      assert processor.validate_name("") is False
      assert processor.validate_name("A" * 1000) is False
      assert processor.validate_name("John Doe") is True
      
      # Collection edge cases
      assert processor.process_tags([]) == []
      assert processor.process_tags(["tag1"]) == ["tag1"]
      assert processor.process_tags(["tag1", "tag2"]) == ["tag1", "tag2"]
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Low overall edge case coverage
  def test_basic_functionality():
      service = DataService()
      
      # Only normal cases, no edge case consideration
      result = service.process_data("normal input")
      assert result is not None
      
      result2 = service.process_list([1, 2, 3])
      assert len(result2) == 3
      
      # Missing: None/empty inputs, boundary values, error conditions
  ```

### PTAS: Assertion Rules

#### PTAS001: Too Few Assertions
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数のアサーション数が推奨される最小値より少ない場合
- **設定**: `min_asserts`（デフォルト: 1）
- **Good Examples**:
  ```python
  # Good: Has at least minimum assertions
  def test_user_creation():
      user = User("John", "john@example.com")
      
      assert user.name == "John"
      assert user.email == "john@example.com"
  
  # Good: Single meaningful assertion
  def test_calculation():
      result = Calculator().add(2, 3)
      assert result == 5
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: No assertions at all
  def test_without_assertions():
      user = User("John")
      user.save()
      # Missing assertions to verify behavior!
  
  # Bad: Only side effects, no verification
  def test_side_effects_only():
      logger = Logger()
      logger.info("Test message")
      # Should assert log was written, state changed, etc.
  ```

#### PTAS002: Too Many Assertions
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数のアサーション数が推奨される最大値より多い場合  
- **設定**: `max_asserts`（デフォルト: 3）
- **Good Examples**:
  ```python
  # Good: Focused test with appropriate assertions
  def test_user_validation():
      user = User("john@example.com", "password123")
      
      assert user.email == "john@example.com"
      assert user.is_valid() is True
      assert user.password_hash is not None
  
  # Good: Split complex test into multiple focused tests
  def test_user_creation():
      user = User("John", "john@example.com")
      assert user.name == "John"
      assert user.email == "john@example.com"
  
  def test_user_validation_rules():
      user = User("john@example.com", "weak")
      assert user.is_password_strong() is False
      assert len(user.validation_errors) > 0
  ```
- **Bad Examples** (would trigger this rule):
  ```python
  # Bad: Too many assertions in single test
  def test_user_everything():
      user = User("John", "john@example.com", "password123")
      assert user.name == "John"
      assert user.email == "john@example.com"
      assert user.password_hash is not None
      assert user.is_valid() is True
      assert user.created_at is not None  # Too many!
      assert user.updated_at is not None
      assert user.is_active is True
  ```

#### PTAS003: High Assertion Density
- **Default Severity**: ERROR (configurable)
- **Description**: コード行数に対するアサーションの割合が高い場合
- **設定**: `max_density`（デフォルト: 0.5）
- **注意**: 通常は集中度の高いテストを示しています
- **Example**:
  ```python
  def test_example():
      result = get_user()
      assert result.name == "John"
      assert result.age == 30
      assert result.active == True
      # High density but acceptable
  ```

#### PTAS004: No Assertions Found
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数にアサーションが全く含まれていない場合
- **修正方法**: 期待される動作を検証するアサーションを追加してください
- **Example**:
  ```python
  # Bad - no verification
  def test_example():
      user = create_user("test")
      user.save()
      # Missing assertions!
  ```

#### PTAS005: Assertion Count OK
- **Default Severity**: ERROR (configurable)
- **Description**: テスト関数が適切な数のアサーションを持っている場合
- **良い例**: アサーション数が推奨範囲内にある場合
- **Example**:
  ```python
  def test_example():
      result = process("test")
      assert result == expected
      # Good - appropriate assertion count
  ```

## System Errors

System errors are handled through standard Python exceptions and do not use rule IDs:

- **ParseError**: Raised when test files cannot be parsed (exit code 2)
- **CheckerError**: Raised when a checker fails to execute (exit code 3)  
- **ConfigurationError**: Raised for invalid configuration (exit code 4)

## Future Rule Categories

### PTPR: Performance Rules (Planned)
- Test execution time warnings
- Resource usage optimization
- Fixture efficiency

### PTDP: Dependency Rules (Planned)
- Mock usage patterns
- Test isolation issues
- Setup/teardown optimization

### PTDC: Documentation Rules (Planned)
- Docstring requirements
- Inline comment quality
- Test description clarity

## Rule ID Format

```
PT[CATEGORY][NUMBER]
│  │        │
│  │        └── 3-digit number (001-999)
│  └── 2-letter category code
└── Pytestee prefix
```

**Categories:**
- **CM**: Comment-based patterns
- **ST**: Structural patterns  
- **LG**: Logical flow patterns
- **AS**: Assertion rules
- **NM**: Naming conventions
- **VL**: Vulnerability detection
- **EC**: Edge case coverage
- **PR**: Performance rules (planned)
- **DP**: Dependencies (planned)
- **DC**: Documentation (planned)

## Configuration

### Rule Selection and Behavior

`pyproject.toml`または`.pytestee.toml`でルールの動作を設定してください：

```toml
[tool.pytestee]
# Rule selection (ruff-like)
select = ["PTCM", "PTAS", "PTEC"]  # Check comment patterns, assertions, and edge cases
ignore = ["PTST002"]               # Ignore pattern not detected warnings

# Rule severity customization
[tool.pytestee.severity]
PTCM001 = "info"      # AAA pattern detected - informational
PTCM002 = "info"      # GWT pattern detected - informational  
PTST001 = "info"      # Structural pattern - informational
PTLG001 = "info"      # Logical pattern - informational
PTAS005 = "info"      # Assertion count OK - informational
PTST002 = "warning"   # Pattern not detected - warning
PTNM001 = "warning"   # Japanese characters in method names - warning
PTAS001 = "warning"   # Too few assertions - warning
PTAS002 = "warning"   # Too many assertions - warning
PTAS004 = "error"     # No assertions found - error (default)
PTEC001 = "warning"   # Numeric edge cases missing - warning
PTEC002 = "warning"   # Collection edge cases missing - warning
PTEC003 = "warning"   # String edge cases missing - warning
PTEC004 = "info"      # Normal/abnormal ratio analysis - informational
PTEC005 = "warning"   # Overall edge case coverage score - warning

# Behavioral thresholds
max_asserts = 5          # PTAS002 threshold
min_asserts = 1          # PTAS001 threshold
require_aaa_comments = true  # Prefer PTCM001/PTCM002 over other patterns
max_density = 0.6        # PTAS003 threshold

# Edge case coverage thresholds
min_numeric_edge_cases = 1      # PTEC001 threshold
min_collection_edge_cases = 1   # PTEC002 threshold  
min_string_edge_cases = 1       # PTEC003 threshold
normal_ratio_target = 0.7       # PTEC004 normal case ratio
abnormal_ratio_target = 0.3     # PTEC004 abnormal case ratio
min_coverage_score = 0.6        # PTEC005 minimum coverage score
```

### Severity Levels

All rules default to **ERROR** severity, but can be configured to:
- **"error"**: Critical issues that should fail CI/CD (exit code 1)
- **"warning"**: Issues that should be addressed but don't fail builds
- **"info"**: Informational messages for good practices detected

### Rule Selection

Similar to ruff, you can select or ignore rules:
- **select**: Only run specified rules (if empty, all rules are selected)
- **ignore**: Never run specified rules (takes precedence over select)

Pattern matching supports:
- Exact rule IDs: `"PTAS004"`
- Category prefixes: `"PTCM"` (matches PTCM001, PTCM002, etc.)
- Multiple categories: `"PT"` (matches all pytestee rules)


## Rule Priority and Conflicts

### Pattern Detection Priority
複数のパターン検出ルールがマッチした場合：
1. **PTCM001/PTCM002**（コメント）- 最高優先度、最も明示的
2. **PTST001**（構造的）- 良好な視覚的分離
3. **PTLG001**（論理的）- 基本的なパターン検出
4. **PTST002**（警告）- パターンが検出されない場合のフォールバック

### Conflicting Rules
一部のルールは相互排他的で、同時に有効にすることはできません：

**パターン検出の競合：**
- PTCM001, PTCM002, PTST001, PTLG001, PTST002は優先順位に従います（真の競合ではありません）

**アサーション数の競合：**
- PTAS001（不足）はPTAS005（適切）と競合
- PTAS002（過多）はPTAS005（適切）と競合
- PTAS004（なし）はPTAS001, PTAS002, PTAS005と競合

**設定の競合：**
- `min_asserts` > `max_asserts`は無効
- `max_density`は0.0から1.0の間である必要があります

## Adding New Rules

新しいルールを貢献する場合：
1. 適切なカテゴリを選択するか、新しいカテゴリを作成
2. カテゴリ内で次に利用可能な番号を使用（001-999）
3. ここに包括的なドキュメントを追加
4. 良いコードと悪いコードの例を含める
5. 閾値の設定オプションを検討
6. CLIヘルプとエラーメッセージを更新

### Category Guidelines
- **PTCM**: コメントによる明示的な開発者の意図
- **PTST**: コード構造と整理
- **PTLG**: コードフローの暗黙のパターン
- **PTAS**: アサーションの量と質
- **PTNM**: テストメソッドの命名規則
- **PTVL**: テストの脆弱性と依存関係の検出
- **PTEC**: エッジケース網羅性とテストパターン分析