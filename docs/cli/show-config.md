# show-config コマンド

現在の設定を表示します。設定ファイル、環境変数、デフォルト値がどのように適用されているかを確認できます。

## 基本構文

```bash
pytestee show-config [OPTIONS]
```

## オプション

### --format, -f
出力フォーマットを指定します。

**値**: `console` | `json`  
**デフォルト**: `console`

=== "console形式"
    ```bash
    pytestee show-config
    ```

=== "JSON形式"
    ```bash
    pytestee show-config --format json
    ```

## 出力例

### console形式

```
Current Configuration:
======================

Config file: /path/to/project/.pytestee.toml

Rule Selection:
  select: ["PTCM", "PTAS"]
  ignore: ["PTST002"]

Rule Severities:
  PTCM001: info
  PTCM002: info
  PTAS001: warning
  PTAS002: warning
  PTAS004: error

Thresholds:
  max_asserts: 3
  min_asserts: 1
  max_density: 0.5

Output Settings:
  format: console
  verbose: false
  show_stats: false

File Filtering:
  include: []
  exclude: ["tests/legacy/*"]
  test_patterns: ["test_*.py", "*_test.py"]
```

### JSON形式

```json
{
  "config_file": "/path/to/project/.pytestee.toml",
  "rule_selection": {
    "select": ["PTCM", "PTAS"],
    "ignore": ["PTST002"]
  },
  "rule_severities": {
    "PTCM001": "info",
    "PTCM002": "info",
    "PTAS001": "warning",
    "PTAS002": "warning",
    "PTAS004": "error"
  },
  "thresholds": {
    "max_asserts": 3,
    "min_asserts": 1,
    "max_density": 0.5,
    "min_numeric_edge_cases": 1,
    "min_collection_edge_cases": 1,
    "min_string_edge_cases": 1,
    "normal_ratio_target": 0.7,
    "abnormal_ratio_target": 0.3,
    "min_coverage_score": 0.6
  },
  "output_settings": {
    "format": "console",
    "verbose": false,
    "show_stats": false,
    "no_color": false
  },
  "file_filtering": {
    "include": [],
    "exclude": ["tests/legacy/*"],
    "test_patterns": ["test_*.py", "*_test.py"],
    "follow_symlinks": false
  }
}
```

## 使用例

### 設定の確認

```bash
# 現在の設定を表示
pytestee show-config

# 設定をJSON形式で表示
pytestee show-config --format json

# 設定をファイルに保存
pytestee show-config --format json > current-config.json
```

### トラブルシューティング

```bash
# 設定が期待通りに読み込まれているか確認
pytestee show-config

# どの設定ファイルが使用されているか確認
pytestee show-config | grep "Config file"

# 環境変数の影響を確認
PYTESTEE_MAX_ASSERTS=10 pytestee show-config
```

### 設定の検証

```bash
# 特定の設定ファイルの内容を確認
pytestee show-config --config custom-config.toml

# デフォルト設定を確認（設定ファイルなし）
mv .pytestee.toml .pytestee.toml.bak
pytestee show-config
mv .pytestee.toml.bak .pytestee.toml
```

## 設定情報の詳細

### 設定ファイルの優先順位

show-configコマンドは以下の順序で設定を読み込みます：

1. コマンドライン引数（最高優先度）
2. 環境変数
3. 設定ファイル
   - `--config`で指定されたファイル
   - `pyproject.toml`
   - `.pytestee.toml`
   - `setup.cfg`
4. デフォルト値（最低優先度）

### 表示される設定項目

| カテゴリ | 説明 |
|----------|------|
| **Rule Selection** | 有効/無効なルールの設定 |
| **Rule Severities** | 各ルールの重要度レベル |
| **Thresholds** | アサーション数やエッジケース閾値 |
| **Output Settings** | 出力フォーマットや詳細度 |
| **File Filtering** | ファイル包含/除外パターン |

### よくある確認項目

!!! tip "設定確認のベストプラクティス"
    
    **新しいプロジェクト設定時**:
    ```bash
    pytestee show-config
    ```
    
    **期待通りのルールが有効か確認**:
    ```bash
    pytestee show-config | grep -A 10 "Rule Selection"
    ```
    
    **閾値設定の確認**:
    ```bash
    pytestee show-config --format json | jq '.thresholds'
    ```
    
    **環境変数の影響確認**:
    ```bash
    env | grep PYTESTEE
    pytestee show-config
    ```

## エラーと解決方法

### 設定ファイルが見つからない

```bash
$ pytestee show-config
Warning: No configuration file found, using defaults

Config file: None (using defaults)
...
```

**解決方法**: `.pytestee.toml`または`pyproject.toml`に設定を追加

### 無効な設定値

```bash
$ pytestee show-config
Error: Invalid configuration: min_asserts (5) must be <= max_asserts (3)
```

**解決方法**: 設定ファイルの値を修正

### 権限エラー

```bash
$ pytestee show-config --config /restricted/config.toml
Error: Permission denied: /restricted/config.toml
```

**解決方法**: ファイルの権限を確認するか、アクセス可能な場所にファイルを配置