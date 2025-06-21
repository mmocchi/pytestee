# pytestee

テストコードの構造的・質的問題を分析するpytest用の品質チェッカーCLIツールです。

## Features

- **AAA/GWT Pattern Detection**: テストがArrange-Act-Assert（準備-実行-検証）またはGiven-When-Then（前提-実行-検証）パターンに従っているかをチェック
- **Assert Density Analysis**: テスト関数ごとの適切なアサーション数と密度を検証
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

## Quick Start

```bash
# カレントディレクトリの全テストファイルをチェック
pytestee check tests/

# 特定のテストファイルをチェック
pytestee check test_example.py

# カスタム制限でチェック
pytestee check tests/ --max-asserts=5 --min-asserts=1

# 詳細情報を表示
pytestee check tests/ --verbose

# JSON出力を取得
pytestee check tests/ --format=json
```

## Usage Examples

### Basic Usage

```bash
# テスト品質を分析
pytestee check tests/

# 出力例:
# ❌ test_user.py::test_create_user
#    - AAAパターンが検出されませんでした (line 15)
#    - アサーションが多すぎます: 5個 (推奨: ≤3個)
#
# ✅ test_auth.py::test_login_success
#    - AAAパターン: OK
#    - アサーション密度: OK (2個のアサーション)
```

### Configuration Options

```bash
# コマンドラインオプション
pytestee check tests/ --max-asserts=3 --min-asserts=1 --require-aaa-comments

# 静寂モード（エラーのみ表示）
pytestee check tests/ --quiet

# 詳細モード（詳細情報を表示）
pytestee check tests/ --verbose
```

### File Information

```bash
# テストファイルの統計を表示
pytestee info tests/

# 利用可能なチェッカーをリスト表示
pytestee list-checkers
```

## Configuration

### Configuration File

`.pytestee.toml`を作成するか、`pyproject.toml`に追加してください：

```toml
[tool.pytestee]
max_asserts = 3
min_asserts = 1
require_aaa_comments = true

[tool.pytestee.pattern_checker]
enabled = true
[tool.pytestee.pattern_checker.config]
require_comments = false
allow_gwt = true

[tool.pytestee.assertion_checker]
enabled = true
[tool.pytestee.assertion_checker.config]
max_asserts = 3
min_asserts = 1
max_density = 0.5
```

### Environment Variables

```bash
export PYTESTEE_MAX_ASSERTS=5
export PYTESTEE_MIN_ASSERTS=1
export PYTESTEE_REQUIRE_AAA_COMMENTS=true
```

## Quality Checkers

### AAA Pattern Checker

Arrange-Act-Assert（準備-実行-検証）またはGiven-When-Then（前提-実行-検証）パターンを以下の方法で検出します：

- **コメントベース検出**: `# Arrange`, `# Act`, `# Assert`
- **構造的分離**: テストセクションを分離する空行
- **コードフロー解析**: セットアップ、実行、検証の論理的グループ化

### Assert Density Checker

アサーションの使用状況を分析します：

- **数量検証**: テストあたりの適切なアサーション数を確保
- **密度分析**: アサーションとコードの比率をチェック
- **複雑度スコアリング**: 過度に複雑なテスト関数を特定

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
from pytestee.domain.interfaces import IChecker
from pytestee.infrastructure.checkers.base_checker import BaseChecker

class MyCustomChecker(BaseChecker):
    def __init__(self):
        super().__init__("my_custom_checker")
    
    def check_function(self, test_function, test_file, config=None):
        # ここにチェックロジックを記述
        return [CheckResult(...)]
```

2. Register the checker:

```python
from pytestee.registry import CheckerRegistry

registry = CheckerRegistry()
registry.register(MyCustomChecker())
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

## Architecture

Pytesteeは、各チェックが個別のルールモジュールとして実装されるルールベースアーキテクチャに従っています：

### Rule Organization

```
src/pytestee/infrastructure/rules/
├── ptcm/          # コメントベースパターン
│   ├── ptcm001.py # コメント内のAAAパターン
│   └── ptcm002.py # コメント内のGWTパターン
├── ptst/          # 構造的パターン
│   ├── ptst001.py # AAA構造的分離
│   └── ptst002.py # パターン未検出警告
├── ptlg/          # 論理フローパターン
│   └── ptlg001.py # AAAコードフロー解析
├── ptas/          # アサーションルール
│   ├── ptas001.py # アサーション不足
│   ├── ptas002.py # アサーション過多
│   ├── ptas003.py # 高いアサーション密度
│   ├── ptas004.py # アサーション未発見
│   └── ptas005.py # アサーション数OK
└── ptsy/          # システムルール
    ├── ptsy001.py # 解析失敗
    └── ptsy002.py # チェッカー失敗
```

### Adding New Rules

1. 適切なカテゴリディレクトリに新しいルールモジュールを作成
2. `BaseRule`を継承し、`check`メソッドを実装
3. 適切なチェッカー（PatternChecker、AssertionChecker等）にルールを追加
4. RULES.mdドキュメントを更新
5. 新しいルールのテストを追加

### Rule Priority

パターン検出は優先順位に従います：
1. **コメントベース** (PTCM) - 最高優先度
2. **構造的** (PTST) - 中程度の優先度
3. **論理的** (PTLG) - 低い優先度
4. **警告** (PTST002) - パターンが検出されない場合のフォールバック

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