# Getting Started with Pytestee

Pytesteeは、pytest形式のテストコードの品質をチェックするCLIツールです。Clean Architectureの原則に基づいて構築されており、ルールベースのアーキテクチャによってテストの品質を評価します。

## インストール

!!! note "要件"
    Python 3.9以上が必要です

=== "pip"
    ```bash
    pip install pytestee
    ```

=== "uv（推奨）"
    ```bash
    uv add pytestee
    ```

=== "pipx（グローバル）"
    ```bash
    pipx install pytestee
    ```

## 基本的な使用方法

### 単一のテストファイルをチェック
```bash
pytestee tests/test_example.py
```

### ディレクトリ内のすべてのテストファイルをチェック
```bash
pytestee tests/
```

### 複数のファイルやディレクトリを指定
```bash
pytestee tests/unit/ tests/integration/test_main.py
```

## 基本的なコマンド

### check コマンド（デフォルト）
```bash
# 以下のコマンドはすべて同等です
pytestee tests/
pytestee check tests/
```

### 出力フォーマットの指定
```bash
# JSON形式で出力
pytestee tests/ --format json

# コンソール形式で出力（デフォルト）
pytestee tests/ --format console
```

### 設定ファイルの指定
```bash
# カスタム設定ファイルを使用
pytestee tests/ --config custom-config.toml
```

### 詳細な出力
```bash
# 詳細なログを表示
pytestee tests/ --verbose

# より詳細なデバッグ情報を表示
pytestee tests/ -vv
```

## 設定

### 設定ファイル

Pytesteeは以下の場所で設定ファイルを自動検索します：

1. `pyproject.toml` の `[tool.pytestee]` セクション
2. `.pytestee.toml`
3. `setup.cfg` の `[pytestee]` セクション

### 基本的な設定例

```toml
[tool.pytestee]
# チェックするルールを選択
select = ["PTCM", "PTAS", "PTEC"]

# 除外するルール
ignore = ["PTST002"]

# ルールの重要度を変更
[tool.pytestee.severity]
PTCM001 = "info"      # AAA パターン検出 - 情報
PTCM002 = "info"      # GWT パターン検出 - 情報  
PTST001 = "info"      # 構造的パターン - 情報
PTAS001 = "warning"   # アサーション不足 - 警告
PTAS002 = "warning"   # アサーション過多 - 警告
PTAS004 = "error"     # アサーションなし - エラー（デフォルト）

# しきい値の設定
max_asserts = 5          # PTAS002 のしきい値
min_asserts = 1          # PTAS001 のしきい値
max_density = 0.6        # PTAS003 のしきい値
```

### 環境変数

設定は環境変数でも指定できます：

```bash
# 詳細出力を有効化
export PYTESTEE_VERBOSE=true

# 設定ファイルのパスを指定
export PYTESTEE_CONFIG="/path/to/config.toml"

# 出力フォーマットを指定
export PYTESTEE_FORMAT="json"
```

## ルールの概要

Pytesteeは以下のカテゴリのルールを提供します：

### PTCM: コメントベースパターン
- **PTCM001**: AAA パターン（Arrange, Act, Assert）の検出
- **PTCM002**: GWT パターン（Given, When, Then）の検出

### PTST: 構造的パターン
- **PTST001**: 空行による構造的な AAA パターンの検出
- **PTST002**: 明確なパターンが検出されない場合の警告

### PTLG: 論理的パターン
- **PTLG001**: AST解析による AAA パターンの検出

### PTAS: アサーション
- **PTAS001**: アサーション不足
- **PTAS002**: アサーション過多
- **PTAS003**: アサーション密度が高い
- **PTAS004**: アサーションが存在しない
- **PTAS005**: 適切なアサーション数

### PTNM: 命名規則
- **PTNM001**: テストメソッド名の日本語文字使用

### PTVL: 脆弱性検出
- **PTVL001**: プライベート属性・メソッドへのアクセス
- **PTVL002**: 時間依存性の検出
- **PTVL003**: ランダム性依存の検出
- **PTVL004**: グローバル状態の変更
- **PTVL005**: クラス変数の操作

### PTEC: エッジケース網羅性
- **PTEC001**: 数値エッジケースの不足
- **PTEC002**: コレクションエッジケースの不足
- **PTEC003**: 文字列エッジケースの不足
- **PTEC004**: 正常・異常ケース比率の分析
- **PTEC005**: 全体的なエッジケース網羅性スコア

詳細については、[ルールリファレンス](rules.md)を参照してください。

## 例

### 良いテストの例

!!! success "推奨パターン"
    ```python
    def test_ユーザー作成():
        """ユーザー作成機能のテスト。"""
        # Arrange
        name = "田中太郎"
        email = "tanaka@example.com"
        
        # Act
        user = User.create(name, email)
        
        # Assert
        assert user.name == name
        assert user.email == email
        assert user.is_valid()
    ```

### 改善が必要なテストの例

!!! warning "要改善パターン"
    ```python
    def test_user_creation():  # PTNM001: 日本語の使用を推奨
        user = User("田中太郎", "tanaka@example.com")  # PTST002: パターン不明確
        # PTAS004: アサーションが不足
    ```
    
    このテストの問題点：
    
    - :material-close: 英語メソッド名（日本語推奨）
    - :material-close: 構造が不明確（AAA/GWTパターンなし）
    - :material-close: アサーションがない

## トラブルシューティング

### よくある問題

!!! question "Q: 設定ファイルが見つからない"
    ```bash
    pytestee tests/ --config .pytestee.toml
    ```

!!! question "Q: 特定のルールを無効化したい"
    ```toml
    [tool.pytestee]
    ignore = ["PTNM001"]  # 日本語命名ルールを無効化
    ```

!!! question "Q: すべてのルールを情報レベルにしたい"
    ```toml
    [tool.pytestee.severity]
    "PT" = "info"  # すべてのルールを情報レベルに
    ```

### ヘルプの表示

```bash
# 全般的なヘルプ
pytestee --help

# checkコマンドのヘルプ
pytestee check --help
```

## 次のステップ

- [ルールリファレンス](rules.md)でより詳細なルール情報を確認
- [設定ガイド](configuration.md)で高度な設定方法を学習
- [CLIリファレンス](cli-reference.md)でコマンドの詳細を確認