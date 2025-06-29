# pytestee

テストコードの構造的・質的問題を分析するpytest用の品質チェッカーCLIツールです。

## Features

- **AAA/GWT Pattern Detection**: テストがArrange-Act-Assert（準備-実行-検証）またはGiven-When-Then（前提-実行-検証）パターンに従っているかをチェック
- **Assert Density Analysis**: テスト関数ごとの適切なアサーション数と密度を検証
- **Per-File Rule Customization**: ファイルやディレクトリごとにルールを個別設定（ruff風の設定）
- **Clean Architecture**: 新しい品質チェッカーを追加するための拡張可能な設計
- **Rich CLI Output**: 詳細な分析結果を表示する美しいコンソール出力
- **Configurable**: ファイルやコマンドラインオプションによる設定サポート

## Installation

```bash
# PyPIからインストール（公開時）
pip install pytestee

# または開発モードでインストール
git clone <repository>
cd pytestee
uv sync
```

## Documentation

詳細なドキュメントは [https://pytestee.readthedocs.io/](https://pytestee.readthedocs.io/) で利用できます。

### Local Documentation Development

```bash
# ドキュメント依存関係をインストール
task install:docs

# ローカルでドキュメントをプレビュー
task docs:serve

# ドキュメントをビルド
task docs:build

# ドキュメントビルド成果物をクリーン
task docs:clean
```

## Quick Start

```bash
# カレントディレクトリの全.pyファイルをチェック（excludeパターンを除く）
pytestee check

# 特定のディレクトリをチェック
pytestee check tests/

# 特定のテストファイルをチェック
pytestee check test_example.py

# 詳細情報を表示
pytestee check --verbose

# JSON出力を取得
pytestee check --format=json

# 設定ファイルを使ってファイル別にルールをカスタマイズ
# .pytestee.tomlに[per_file_ignores]を設定後:
pytestee check  # ファイル別無視設定が自動適用される
```

## Usage Examples

### Basic Usage

```bash
# カレントディレクトリのテスト品質を分析
pytestee check

# 特定ディレクトリのテスト品質を分析
pytestee check tests/

# 出力例:
# ❌ test_user.py::test_create_user
#    - PTST002: AAAパターンが検出されませんでした (line 15)
#    - PTAS002: アサーションが多すぎます: 5個 (推奨: ≤3個)
#
# ✅ test_auth.py::test_login_success
#    - PTCM001: AAAパターンがコメントで明示されています
#    - PTAS005: アサーション数が適切です (2個)
```

### Configuration Options

```bash
# 静寂モード（エラーのみ表示）
pytestee check tests/ --quiet

# 詳細モード（詳細情報を表示）
pytestee check tests/ --verbose
```

### File Information

```bash
# カレントディレクトリのテストファイルの統計を表示
pytestee info

# 特定ディレクトリのテストファイルの統計を表示
pytestee info tests/

# 利用可能なチェッカーをリスト表示
pytestee list-checkers
```

## Configuration

### Default Rule Selection

pytesteeは以下のルールをデフォルトで有効にしています：

- **PTCM003**: AAAまたはGWTパターン検出（コメントベース）
- **PTST001**: 構造的分離による暗黙的なAAAパターン検出
- **PTLG001**: 論理フロー解析によるAAAパターン検出
- **PTAS005**: アサーション数が適切な範囲内
- **PTNM001**: テストメソッド名の日本語文字チェック
- **PTVL001**: プライベート属性・メソッドアクセス検出
- **PTVL002**: 時間依存コード検出

この選択は以下の理由に基づいています：
- **実用性**: 最も一般的で重要な問題を検出
- **競合回避**: 重複する機能のルール（例：PTAS001/002/004 vs PTAS005）は片方のみ選択
- **段階的導入**: 新しいルールカテゴリ（PTVL）は段階的に導入

### Configuration File

`.pytestee.toml`を作成するか、`pyproject.toml`に追加してください：

```toml
[tool.pytestee]
# ファイル選択パターン
# デフォルトでは全ての.pyファイルが対象
exclude = ["**/conftest.py", "**/test_fixtures/**"]  # 除外するファイルパターン

# 有効にするルールを選択（以下がデフォルト選択）
select = ["PTCM003", "PTST001", "PTLG001", "PTAS005", "PTNM001", "PTVL001", "PTVL002"]

# 無視するルール
ignore = ["PTLG001"]  # 論理フロー解析を無効化

# ルールごとの重要度をカスタマイズ
[tool.pytestee.severity]
PTAS002 = "warning"  # アサーション過多を警告レベルに
PTNM001 = "info"     # 日本語命名チェックを情報レベルに

# ルール固有の設定
[tool.pytestee.rules.PTAS005]
max_asserts = 3
min_asserts = 1

[tool.pytestee.rules.PTCM003]
require_comments = false
allow_gwt = true

[tool.pytestee.rules.PTAS003]
max_density = 0.5
```

### Per-File Ignores

特定のファイルやディレクトリに対してルールを無視したい場合、`per_file_ignores`設定を使用できます（ruff風の設定）：

```toml
[tool.pytestee]
# グローバルルール設定
select = ["PTCM001", "PTAS005", "PTNM001"]

# ファイル別無視設定
[tool.pytestee.per_file_ignores]
"tests/unit/**" = ["PTCM001"]                    # ユニットテストはAAAコメント不要
"tests/integration/**" = ["PTAS005"]             # 統合テストはアサーション数制限なし
"**/conftest.py" = ["PTCM001", "PTAS005"]       # conftest.pyは全体的に緩い
"**/__init__.py" = ["PTNM001"]                  # __init__.pyは命名ルール緩い
"tests/fixtures/**" = ["PTCM001", "PTAS005"]    # フィクスチャファイルは緩い
```

#### サポートパターン

- **完全一致**: `"conftest.py"` - ファイル名の完全一致
- **ディレクトリワイルドカード**: `"tests/**"` - ディレクトリとその全サブディレクトリ
- **ファイルパターン**: `"**/test_*.py"` - 任意の深さのtest_で始まるファイル
- **複合パターン**: `"tests/unit/**/test_*.py"` - 複数の条件の組み合わせ

#### 使用例

```bash
# この設定では以下のような動作になります:

# tests/unit/test_user.py - PTCM001が無視される
pytestee check tests/unit/test_user.py

# tests/integration/test_api.py - PTAS005が無視される  
pytestee check tests/integration/test_api.py

# src/myapp/__init__.py - PTNM001が無視される
pytestee check src/myapp/__init__.py

# 通常のファイル - 全ルールが適用される
pytestee check src/myapp/service.py
```


## Quality Rules

### パターン検出ルール

- **PTCM001**: コメント内のAAAパターン検出 (`# Arrange`, `# Act`, `# Assert`)
- **PTCM002**: コメント内のGWTパターン検出 (`# Given`, `# When`, `# Then`)
- **PTCM003**: AAAまたはGWTパターン検出（どちらかが存在すればOK）
- **PTST001**: 構造的分離による暗黙的なAAAパターン検出（空行での分離）
- **PTST002**: パターン未検出の警告
- **PTLG001**: 論理フロー解析によるAAAパターン検出（コードの意味解析）

### アサーションルール

- **PTAS001**: アサーション不足（最小数未満）
- **PTAS002**: アサーション過多（最大数超過）
- **PTAS003**: 高いアサーション密度の警告
- **PTAS004**: アサーション未発見エラー
- **PTAS005**: アサーション数が適切な範囲内

### 命名規則ルール

- **PTNM001**: テストメソッド名の日本語文字チェック

### 脆弱性検出ルール（PTVL）

- **PTVL001**: プライベート属性・メソッドアクセス検出（デフォルト有効）
- **PTVL002**: 時間依存コード検出（`datetime.now()`, `time.time()`等）（デフォルト有効）
- **PTVL003**: ランダム依存コード検出（`random()`関数等）
- **PTVL004**: グローバル状態変更検出
- **PTVL005**: クラス変数操作検出

## Architecture

Clean Architectureの原則に基づいて構築されています：

```
src/pytestee/
├── domain/          # ビジネスロジックとモデル
├── usecases/        # アプリケーションロジック
├── adapters/        # 外部インターフェース (CLI、リポジトリ、プレゼンター)
├── infrastructure/  # 具体実装 (AST解析、チェッカー)
└── registry.py      # 依存性注入コンテナ
```

### Adding Custom Checkers

1. Implement the `IChecker` interface:

```python
from pytestee.domain.rules.base_rule import BaseRule
from pytestee.domain.models import CheckResult, TestFunction, TestFile
from typing import Optional

class MyCustomRule(BaseRule):
    def __init__(self):
        super().__init__(
            rule_id="MYCUST001",
            name="my_custom_rule",
            description="カスタムルールの説明"
        )
    
    def check(self, test_function: TestFunction, test_file: TestFile, 
              config: Optional[CheckerConfig] = None) -> CheckResult:
        # ここにチェックロジックを記述
        if self._check_condition(test_function):
            return self._create_success_result(
                "チェック成功", test_file, test_function
            )
        return self._create_failure_result(
            "チェック失敗", test_file, test_function
        )
```

2. ルールを適切なチェッカーに追加:

```python
# 例: PatternCheckerに追加する場合
from pytestee.infrastructure.checkers.pattern_checker import PatternChecker

pattern_checker = PatternChecker()
pattern_checker.add_rule(MyCustomRule())
```

## Development

### Setup

```bash
# ツール管理のためのmiseをインストール
mise install

# 依存関係をインストール
task install

# テストを実行
task test

# リンティングを実行
task lint

# コードをフォーマット
task format

# パッケージをビルド
task build
```

### Project Tasks

- `task install` - 依存関係をインストール
- `task test` - テストスイートを実行
- `task lint` - リンティングを実行 (ruff + mypy)
- `task format` - コードをフォーマット
- `task build` - パッケージをビルド
- `task clean` - ビルド成果物をクリーンアップ

## Rule-Based Architecture

Pytesteeは、各品質チェックが個別のルールモジュールとして実装されるルールベースアーキテクチャに従っています。各ルールには一意のIDがあり、Return Object Patternを使用してCheckSuccessまたはCheckFailureを返します：

### Rule Organization

```
src/pytestee/domain/rules/
├── comment/        # コメントベースパターン
│   ├── aaa_comment_pattern.py    # PTCM001: コメント内のAAAパターン
│   ├── gwt_comment_pattern.py    # PTCM002: コメント内のGWTパターン
│   └── aaa_or_gwt_pattern.py     # PTCM003: AAAまたはGWTパターン
├── structure/      # 構造的パターン
│   ├── structural_pattern.py     # PTST001: AAA構造的分離
│   └── no_pattern_warning.py     # PTST002: パターン未検出警告
├── logic/          # 論理フローパターン
│   └── logical_flow_pattern.py   # PTLG001: AAAコードフロー解析
├── assertion/      # アサーションルール
│   ├── too_few_assertions.py     # PTAS001: アサーション不足
│   ├── too_many_assertions.py    # PTAS002: アサーション過多
│   ├── high_assertion_density.py # PTAS003: 高いアサーション密度
│   ├── no_assertions.py          # PTAS004: アサーション未発見
│   └── assertion_count_ok.py     # PTAS005: アサーション数OK
├── naming/         # 命名規則
│   └── japanese_characters.py     # PTNM001: 日本語文字チェック
└── vulnerability/  # 脆弱性検出
    ├── ptvl001.py                 # PTVL001: プライベートアクセス検出
    ├── ptvl002.py                 # PTVL002: 時間依存検出
    ├── ptvl003.py                 # PTVL003: ランダム依存検出
    ├── ptvl004.py                 # PTVL004: グローバル状態変更検出
    └── ptvl005.py                 # PTVL005: クラス変数操作検出
```

### Adding New Rules

1. 適切なカテゴリディレクトリに新しいルールモジュールを作成
2. `BaseRule`を継承し、`check`メソッドを実装
3. 適切なチェッカー（PatternChecker、AssertionChecker等）にルールを追加
4. RULES.mdドキュメントを更新
5. 新しいルールのテストを追加

### Pattern Detection Priority

パターン検出は優先順位に従います：
1. **コメントベース** (PTCM) - 最高優先度
2. **構造的** (PTST) - 中程度の優先度
3. **論理的** (PTLG) - 低い優先度
4. **警告** (PTST002) - パターンが検出されない場合のフォールバック

優先度の高いパターンが検出された場合、低い優先度のパターンは報告されません。

## Contributing

1. リポジトリをフォーク
2. フィーチャーブランチを作成
3. 変更を実施
4. 新機能にテストを追加
5. テストスイートとリンティングを実行
6. プルリクエストを提出

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] 追加のパターンチェッカー（Page Object、Builder等）
- [ ] 人気のCI/CDシステムとの統合
- [ ] VS Code拡張機能
- [ ] テストカバレッジ分析
- [ ] パフォーマンスベンチマーク
- [ ] カスタムルール設定DSL
- [ ] より多くの言語固有命名ルール（中国語、韓国語など）