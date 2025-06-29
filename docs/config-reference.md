# Configuration Reference

Pytesteeの設定ファイルの完全なリファレンスです。すべての設定オプション、デフォルト値、使用例について詳しく説明します。

## 設定ファイルの種類

Pytesteeは以下の設定ファイルに対応しています：

1. **`pyproject.toml`** - `[tool.pytestee]` セクション（推奨）
2. **`.pytestee.toml`** - 専用設定ファイル
3. **`setup.cfg`** - `[pytestee]` セクション

## 基本設定

### select

チェックするルールを明示的に指定します。

**型**: `list[str]`  
**デフォルト**: `[]`（すべてのルールを選択）

```toml
[tool.pytestee]
# 特定のルールのみ
select = ["PTAS004", "PTCM001"]

# カテゴリ全体
select = ["PTCM", "PTAS"]

# すべてのルール
select = ["PT"]

# 空の場合はすべてのルールが選択される
select = []
```

### ignore

除外するルールを指定します。`select`よりも優先されます。

**型**: `list[str]`  
**デフォルト**: `[]`

```toml
[tool.pytestee]
# 特定のルールを除外
ignore = ["PTST002"]

# カテゴリ全体を除外
ignore = ["PTEC"]

# 複数ルールを除外
ignore = ["PTST002", "PTNM001", "PTEC001"]
```

### format

出力フォーマットを指定します。

**型**: `str`  
**値**: `"console"` | `"json"`  
**デフォルト**: `"console"`

```toml
[tool.pytestee]
format = "console"  # コンソール形式
# format = "json"   # JSON形式
```

### verbose

詳細な出力を有効にします。

**型**: `bool`  
**デフォルト**: `false`

```toml
[tool.pytestee]
verbose = true
```

### show_stats

実行統計を表示します。

**型**: `bool`  
**デフォルト**: `false`

```toml
[tool.pytestee]
show_stats = true
```

### exclude

除外するパスパターンを指定します。

**型**: `list[str]`  
**デフォルト**: `[]`

```toml
[tool.pytestee]
exclude = [
    "tests/legacy/*",
    "**/conftest.py",
    "tests/fixtures/*"
]
```

### include

含めるパスパターンを指定します。

**型**: `list[str]`  
**デフォルト**: `[]`（すべてのパスを含める）

```toml
[tool.pytestee]
include = [
    "tests/unit/*",
    "tests/integration/*"
]
```

## ルール重要度設定

### severity

各ルールの重要度レベルを設定します。

**型**: `dict[str, str]`  
**値**: `"error"` | `"warning"` | `"info"`  
**デフォルト**: すべてのルールが `"error"`

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

# 重要な問題はエラーレベル
PTAS004 = "error"     # アサーションなし
PTVL001 = "error"     # プライベートアクセス
```

### カテゴリ一括設定

カテゴリ全体の重要度を一括で設定できます。

```toml
[tool.pytestee.severity]
# カテゴリ全体を警告レベルに
"PTEC" = "warning"    # すべてのエッジケースルール

# すべてのルールを情報レベルに（開発時）
"PT" = "info"
```

## アサーション関連設定

### max_asserts

アサーションの最大数を設定します（PTAS002のしきい値）。

**型**: `int`  
**デフォルト**: `3`

```toml
[tool.pytestee]
max_asserts = 5  # 最大5個のアサーションまで許可
```

### min_asserts

アサーションの最小数を設定します（PTAS001のしきい値）。

**型**: `int`  
**デフォルト**: `1`

```toml
[tool.pytestee]
min_asserts = 2  # 最低2個のアサーションが必要
```

### max_density

アサーション密度の上限を設定します（PTAS003のしきい値）。

**型**: `float`  
**範囲**: `0.0` - `1.0`  
**デフォルト**: `0.5`

```toml
[tool.pytestee]
max_density = 0.6  # コード行数の60%までのアサーション密度
```

### require_aaa_comments

AAAコメントパターンを優先するかどうかを設定します。

**型**: `bool`  
**デフォルト**: `false`

```toml
[tool.pytestee]
require_aaa_comments = true  # AAA/GWTコメントパターンを優先
```

## エッジケース網羅性設定

### min_numeric_edge_cases

数値エッジケースの最小数を設定します（PTEC001のしきい値）。

**型**: `int`  
**デフォルト**: `1`

```toml
[tool.pytestee]
min_numeric_edge_cases = 2  # 最低2個の数値エッジケースが必要
```

### min_collection_edge_cases

コレクションエッジケースの最小数を設定します（PTEC002のしきい値）。

**型**: `int`  
**デフォルト**: `1`

```toml
[tool.pytestee]
min_collection_edge_cases = 2  # 最低2個のコレクションエッジケースが必要
```

### min_string_edge_cases

文字列エッジケースの最小数を設定します（PTEC003のしきい値）。

**型**: `int`  
**デフォルト**: `1`

```toml
[tool.pytestee]
min_string_edge_cases = 2  # 最低2個の文字列エッジケースが必要
```

### normal_ratio_target

正常ケースの目標比率を設定します（PTEC004の分析用）。

**型**: `float`  
**範囲**: `0.0` - `1.0`  
**デフォルト**: `0.7`

```toml
[tool.pytestee]
normal_ratio_target = 0.8  # 正常ケース80%を目標
```

### abnormal_ratio_target

異常ケースの目標比率を設定します（PTEC004の分析用）。

**型**: `float`  
**範囲**: `0.0` - `1.0`  
**デフォルト**: `0.3`

```toml
[tool.pytestee]
abnormal_ratio_target = 0.2  # 異常ケース20%を目標
```

### min_coverage_score

エッジケース網羅性スコアの最小値を設定します（PTEC005のしきい値）。

**型**: `float`  
**範囲**: `0.0` - `1.0`  
**デフォルト**: `0.6`

```toml
[tool.pytestee]
min_coverage_score = 0.8  # 網羅性スコア80%以上が必要
```

## ファイル処理設定

### test_patterns

テストファイルとして認識するパターンを設定します。

**型**: `list[str]`  
**デフォルト**: `["test_*.py", "*_test.py"]`

```toml
[tool.pytestee]
test_patterns = [
    "test_*.py",
    "*_test.py",
    "tests_*.py"  # カスタムパターンを追加
]
```

### follow_symlinks

シンボリックリンクを追跡するかどうかを設定します。

**型**: `bool`  
**デフォルト**: `false`

```toml
[tool.pytestee]
follow_symlinks = true
```

## 設定例

### 新規プロジェクト（厳格設定）

```toml
[tool.pytestee]
# すべてのルールを有効
select = ["PT"]

# 厳格なしきい値
max_asserts = 3
min_asserts = 1
max_density = 0.4
min_coverage_score = 0.8

# エッジケース要件を厳しく
min_numeric_edge_cases = 2
min_collection_edge_cases = 2
min_string_edge_cases = 2

[tool.pytestee.severity]
# パターン検出は情報
PTCM001 = "info"
PTCM002 = "info"
PTST001 = "info"
PTLG001 = "info"
PTAS005 = "info"

# その他はすべてエラー
PTST002 = "error"
PTAS001 = "error"
PTAS002 = "error"
PTAS004 = "error"
"PTEC" = "error"
"PTVL" = "error"
```

### レガシープロジェクト（段階的導入）

```toml
[tool.pytestee]
# 重要な問題のみ
select = ["PTAS004", "PTVL001", "PTVL002"]

# パターン警告は無視
ignore = ["PTST002"]

# 緩いしきい値
max_asserts = 10
min_asserts = 0
max_density = 0.8

[tool.pytestee.severity]
# アサーションなしは警告レベル
PTAS004 = "warning"

# 脆弱性は情報レベル
"PTVL" = "info"
```

### 開発環境（情報収集）

```toml
[tool.pytestee]
# すべてのルールを実行
select = ["PT"]

# 統計情報を表示
show_stats = true
verbose = true
format = "json"

[tool.pytestee.severity]
# すべて情報レベル
"PT" = "info"
```

### CI/CD環境

```toml
[tool.pytestee]
# コメント・アサーション・脆弱性のみ
select = ["PTCM", "PTAS", "PTVL"]

# 統計表示
show_stats = true
format = "json"

# レガシーファイルを除外
exclude = [
    "tests/legacy/*",
    "tests/fixtures/*"
]

[tool.pytestee.severity]
# パターン検出は情報
PTCM001 = "info"
PTCM002 = "info"

# アサーション・脆弱性はエラー
"PTAS" = "error"
"PTVL" = "error"
```

### チーム開発環境

```toml
[tool.pytestee]
# バランスの取れたルール選択
select = ["PTCM", "PTAS", "PTNM", "PTVL"]

# 日本語命名を推奨
ignore = []

# 適度なしきい値
max_asserts = 5
min_asserts = 1
max_density = 0.6

[tool.pytestee.severity]
# パターン検出は情報
PTCM001 = "info"
PTCM002 = "info"

# 命名は警告
PTNM001 = "warning"

# アサーション・脆弱性はエラー
"PTAS" = "error"
"PTVL" = "error"
```

## 設定の検証

### 設定ファイルの妥当性確認

```bash
# 設定ファイルの構文チェック
pytestee --check-config

# 現在の設定を表示
pytestee show-config

# JSON形式で設定を表示
pytestee show-config --format json
```

### よくある設定エラー

#### 1. 競合するしきい値

```toml
# ❌ エラー: min_asserts > max_asserts
[tool.pytestee]
min_asserts = 5
max_asserts = 3
```

#### 2. 無効な重要度レベル

```toml
# ❌ エラー: 無効なレベル
[tool.pytestee.severity]
PTAS001 = "critical"  # "error", "warning", "info" のみ有効
```

#### 3. 存在しないルールID

```toml
# ❌ エラー: 存在しないルール
[tool.pytestee]
select = ["PTXX001"]
```

#### 4. 無効な数値範囲

```toml
# ❌ エラー: 範囲外の値
[tool.pytestee]
max_density = 1.5     # 0.0-1.0の範囲
min_coverage_score = -0.1  # 0.0-1.0の範囲
```

## 環境変数との関係

設定ファイルの値は環境変数で上書きできます：

```bash
# 設定ファイルで max_asserts = 3 でも、環境変数が優先される
export PYTESTEE_MAX_ASSERTS=5
pytestee tests/  # max_asserts = 5 として実行
```

## 設定の優先順位

1. **コマンドライン引数**（最高優先度）
2. **環境変数**
3. **設定ファイル**（最低優先度）

```toml
# .pytestee.toml
[tool.pytestee]
max_asserts = 3
```

```bash
# 環境変数で上書き
export PYTESTEE_MAX_ASSERTS=5

# コマンドライン引数で最終上書き
pytestee tests/ --max-asserts 7  # 結果: max_asserts = 7
```