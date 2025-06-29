# Configuration Guide

Pytesteeの設定について詳しく説明します。設定により、チェックするルール、重要度レベル、しきい値などをカスタマイズできます。

## 設定ファイルの場所

Pytesteeは以下の順序で設定ファイルを検索します：

1. コマンドラインで指定されたファイル（`--config`オプション）
2. `pyproject.toml` の `[tool.pytestee]` セクション
3. `.pytestee.toml`
4. `setup.cfg` の `[pytestee]` セクション

## 基本的な設定

### pyproject.toml での設定

```toml
[tool.pytestee]
# ルール選択
select = ["PTCM", "PTAS"]  # コメントパターンとアサーションのみチェック
ignore = ["PTST002"]       # パターン未検出警告を無視

# 出力設定
format = "console"         # console | json
verbose = false

# ファイルフィルタリング
exclude = ["tests/legacy/"]
include = ["tests/"]
```

### .pytestee.toml での設定

```toml
# ルール選択
select = ["PTCM", "PTAS", "PTEC"]
ignore = ["PTST002", "PTNM001"]

# 重要度設定
[severity]
PTCM001 = "info"
PTCM002 = "info"
PTST001 = "info"
PTAS001 = "warning"
PTAS002 = "warning"
PTAS004 = "error"

# しきい値設定
max_asserts = 5
min_asserts = 1
max_density = 0.6
```

## ルール選択

### select オプション

チェックするルールを明示的に指定します。

```toml
[tool.pytestee]
# 特定のルールのみ
select = ["PTCM001", "PTAS004"]

# カテゴリ全体を選択
select = ["PTCM", "PTAS"]

# すべてのルールを選択（デフォルト）
select = ["PT"]

# 空の場合はすべてのルールが選択される
select = []
```

### ignore オプション

特定のルールを除外します。`select`よりも優先されます。

```toml
[tool.pytestee]
# 特定のルールを除外
ignore = ["PTST002", "PTNM001"]

# カテゴリ全体を除外
ignore = ["PTEC"]

# パターンマッチング
ignore = ["PTAS*"]  # PTAS001, PTAS002, etc.
```

## 重要度レベル

各ルールの重要度レベルを設定できます。

### 利用可能なレベル

- **error**: 重要なエラー（終了コード1）
- **warning**: 警告（継続実行）
- **info**: 情報（良いパターンの検出）

### 設定例

```toml
[tool.pytestee.severity]
# パターン検出は情報レベル
PTCM001 = "info"      # AAA パターン検出
PTCM002 = "info"      # GWT パターン検出
PTST001 = "info"      # 構造的パターン
PTLG001 = "info"      # 論理的パターン
PTAS005 = "info"      # 適切なアサーション数

# 改善が必要な項目は警告レベル
PTST002 = "warning"   # パターン未検出
PTNM001 = "warning"   # 日本語命名推奨
PTAS001 = "warning"   # アサーション不足
PTAS002 = "warning"   # アサーション過多
PTEC001 = "warning"   # エッジケース不足

# 重要な問題はエラーレベル
PTAS004 = "error"     # アサーションなし
PTVL001 = "error"     # プライベートアクセス
PTVL002 = "error"     # 時間依存
```

### カテゴリ全体の設定

```toml
[tool.pytestee.severity]
# すべてのエッジケースルールを警告に
"PTEC" = "warning"

# すべての脆弱性ルールをエラーに
"PTVL" = "error"

# すべてのルールを情報レベルに（開発時）
"PT" = "info"
```

## しきい値設定

各ルールのしきい値をカスタマイズできます。

### アサーション関連

```toml
[tool.pytestee]
# PTAS001: 最小アサーション数
min_asserts = 1

# PTAS002: 最大アサーション数
max_asserts = 3

# PTAS003: アサーション密度の上限
max_density = 0.5

# AAA コメントパターンを優先するか
require_aaa_comments = true
```

### エッジケース網羅性

```toml
[tool.pytestee]
# PTEC001: 数値エッジケースの最小数
min_numeric_edge_cases = 2

# PTEC002: コレクションエッジケースの最小数
min_collection_edge_cases = 2

# PTEC003: 文字列エッジケースの最小数
min_string_edge_cases = 2

# PTEC004: 正常・異常ケース比率
normal_ratio_target = 0.7
abnormal_ratio_target = 0.3

# PTEC005: 全体的な網羅性スコアの最小値
min_coverage_score = 0.6
```

## ファイルフィルタリング

### include と exclude

```toml
[tool.pytestee]
# チェック対象に含めるパス
include = ["tests/", "src/tests/"]

# チェック対象から除外するパス
exclude = [
    "tests/legacy/",
    "tests/fixtures/",
    "**/conftest.py"
]
```

### ファイル名パターン

```toml
[tool.pytestee]
# テストファイルのパターン（デフォルト）
test_patterns = [
    "test_*.py",
    "*_test.py"
]
```

## 出力設定

### フォーマット

```toml
[tool.pytestee]
# 出力フォーマット
format = "console"  # console | json

# 詳細出力
verbose = true

# 統計情報の表示
show_stats = true

# カラー出力の制御
color = "auto"  # auto | always | never
```

### JSON出力の詳細設定

```toml
[tool.pytestee]
format = "json"

# JSON出力の詳細レベル
json_detail = "full"  # minimal | standard | full

# JSON出力のインデント
json_indent = 2
```

## 環境変数

コマンドライン実行時に環境変数で設定を上書きできます：

```bash
# 詳細出力
export PYTESTEE_VERBOSE=true

# 設定ファイルのパス
export PYTESTEE_CONFIG="/path/to/config.toml"

# 出力フォーマット
export PYTESTEE_FORMAT="json"

# ルール選択（カンマ区切り）
export PYTESTEE_SELECT="PTCM,PTAS"

# ルール除外（カンマ区切り）
export PYTESTEE_IGNORE="PTST002,PTNM001"

# しきい値設定
export PYTESTEE_MAX_ASSERTS=5
export PYTESTEE_MIN_ASSERTS=1
```

## プロジェクト固有の設定例

### 新規プロジェクト（厳格）

```toml
[tool.pytestee]
select = ["PT"]  # すべてのルールを有効

[tool.pytestee.severity]
# パターン検出は情報
PTCM001 = "info"
PTCM002 = "info"
PTST001 = "info"
PTLG001 = "info"
PTAS005 = "info"

# その他はすべてエラー
"PTST002" = "error"
"PTAS001" = "error"
"PTAS002" = "error"
"PTAS004" = "error"
"PTEC" = "error"
"PTVL" = "error"

# 厳格なしきい値
max_asserts = 3
min_asserts = 1
min_coverage_score = 0.8
```

### レガシープロジェクト（段階的導入）

```toml
[tool.pytestee]
select = ["PTAS004", "PTVL"]  # 重要な問題のみ
ignore = ["PTST002"]          # パターン警告は無視

[tool.pytestee.severity]
# アサーションなしのみエラー
PTAS004 = "error"

# 脆弱性は警告レベル
"PTVL" = "warning"

# 緩いしきい値
max_asserts = 10
min_asserts = 0
```

### 開発環境（情報収集）

```toml
[tool.pytestee]
select = ["PT"]
format = "json"

[tool.pytestee.severity]
# すべて情報レベル
"PT" = "info"

# 統計情報を重視
show_stats = true
verbose = true
```

## 設定の検証

設定ファイルの妥当性をチェックできます：

```bash
# 設定ファイルの構文チェック
pytestee --check-config

# 現在の設定を表示
pytestee --show-config

# 利用可能なルール一覧
pytestee --list-rules
```

## トラブルシューティング

### よくある設定エラー

1. **競合するしきい値**
   ```toml
   # エラー: min_asserts > max_asserts
   min_asserts = 5
   max_asserts = 3
   ```

2. **無効な重要度レベル**
   ```toml
   [tool.pytestee.severity]
   PTAS001 = "critical"  # エラー: 無効なレベル
   ```

3. **存在しないルールID**
   ```toml
   [tool.pytestee]
   select = ["PTXX001"]  # エラー: 存在しないルール
   ```

### デバッグ方法

```bash
# 設定のデバッグ出力
pytestee tests/ --verbose --show-config

# 適用されるルールの確認
pytestee tests/ --dry-run

# 設定ファイルの場所を確認
pytestee tests/ --debug
```