# CLI Reference

Pytesteeのコマンドライン インターフェース（CLI）の完全なリファレンスです。

## 基本構文

```bash
pytestee [COMMAND] [OPTIONS] [PATHS...]
```

## グローバルオプション

### --help, -h
ヘルプメッセージを表示して終了します。

```bash
pytestee --help
pytestee -h
```

### --version
バージョン情報を表示して終了します。

```bash
pytestee --version
```

## Commands

### check（デフォルト）

テストファイルの品質をチェックします。これがデフォルトのコマンドなので、省略可能です。

```bash
pytestee check [OPTIONS] [PATHS...]
pytestee [OPTIONS] [PATHS...]  # checkは省略可能
```

#### OPTIONS

##### --format, -f
出力フォーマットを指定します。

**値**: `console` | `json`  
**デフォルト**: `console`

```bash
# コンソール形式（デフォルト）
pytestee tests/ --format console

# JSON形式
pytestee tests/ --format json
```

**console形式の例**:
```
tests/test_example.py:15:5: PTAS004 [ERROR] No assertions found in test function
tests/test_example.py:25:5: PTCM001 [INFO] AAA pattern detected in comments
```

**JSON形式の例**:
```json
{
  "files": [
    {
      "path": "tests/test_example.py",
      "results": [
        {
          "rule_id": "PTAS004",
          "severity": "error",
          "message": "No assertions found in test function",
          "line": 15,
          "column": 5
        }
      ]
    }
  ],
  "summary": {
    "total_files": 1,
    "total_issues": 1,
    "errors": 1,
    "warnings": 0,
    "info": 0
  }
}
```

##### --config, -c
設定ファイルのパスを指定します。

**デフォルト**: 自動検索（`pyproject.toml`, `.pytestee.toml`, `setup.cfg`）

```bash
pytestee tests/ --config custom-config.toml
pytestee tests/ -c .pytestee.toml
```

##### --select
実行するルールを明示的に指定します。

**値**: ルールID、カテゴリ、またはカンマ区切りのリスト

```bash
# 特定のルールのみ
pytestee tests/ --select PTAS004

# カテゴリ全体
pytestee tests/ --select PTCM,PTAS

# 複数ルール
pytestee tests/ --select PTCM001,PTAS001,PTAS004
```

##### --ignore
除外するルールを指定します。

**値**: ルールID、カテゴリ、またはカンマ区切りのリスト

```bash
# 特定のルールを除外
pytestee tests/ --ignore PTST002

# カテゴリ全体を除外
pytestee tests/ --ignore PTEC

# 複数ルールを除外
pytestee tests/ --ignore PTST002,PTNM001
```

##### --verbose, -v
詳細な出力を有効にします。複数指定でより詳細になります。

```bash
pytestee tests/ --verbose
pytestee tests/ -v
pytestee tests/ -vv  # より詳細
```

##### --quiet, -q
出力を最小限に抑えます。

```bash
pytestee tests/ --quiet
pytestee tests/ -q
```

##### --show-stats
実行統計を表示します。

```bash
pytestee tests/ --show-stats
```

出力例:
```
Statistics:
  Files checked: 25
  Total issues: 127
  Errors: 15
  Warnings: 89
  Info: 23
  
Rule frequency:
  PTCM001: 45 (35.4%)
  PTAS001: 23 (18.1%)
  PTST002: 15 (11.8%)
```

##### --exclude
除外するパスパターンを指定します。

**値**: glob パターンのカンマ区切りリスト

```bash
pytestee tests/ --exclude "tests/legacy/*,**/conftest.py"
```

##### --include
含めるパスパターンを指定します。

**値**: glob パターンのカンマ区切りリスト

```bash
pytestee tests/ --include "tests/unit/*,tests/integration/*"
```

##### --max-asserts
アサーションの最大数を設定します（PTAS002のしきい値）。

**値**: 正の整数  
**デフォルト**: 3

```bash
pytestee tests/ --max-asserts 5
```

##### --min-asserts
アサーションの最小数を設定します（PTAS001のしきい値）。

**値**: 0以上の整数  
**デフォルト**: 1

```bash
pytestee tests/ --min-asserts 2
```

##### --no-color
カラー出力を無効にします。

```bash
pytestee tests/ --no-color
```

##### --exit-zero
エラーが見つかっても終了コード0で終了します。

```bash
pytestee tests/ --exit-zero
```

#### PATHS

チェック対象のファイルまたはディレクトリのパスを指定します。複数指定可能です。

```bash
# 単一ファイル
pytestee tests/test_example.py

# ディレクトリ
pytestee tests/

# 複数パス
pytestee tests/unit/ tests/integration/ src/tests/
```

**デフォルト**: カレントディレクトリ（`.`）

### show-config

現在の設定を表示します。

```bash
pytestee show-config [OPTIONS]
```

#### OPTIONS

##### --format, -f
出力フォーマットを指定します。

**値**: `console` | `json`  
**デフォルト**: `console`

```bash
pytestee show-config --format json
```

### list-rules

利用可能なルール一覧を表示します。

```bash
pytestee list-rules [OPTIONS]
```

#### OPTIONS

##### --format, -f
出力フォーマットを指定します。

**値**: `console` | `json`  
**デフォルト**: `console`

##### --category, -c
特定のカテゴリのルールのみ表示します。

**値**: ルールカテゴリ（PTCM, PTST, PTLG, PTAS, PTNM, PTVL, PTEC）

```bash
pytestee list-rules --category PTAS
```

## 終了コード

Pytesteeは以下の終了コードを返します：

| コード | 意味 |
|--------|------|
| 0 | 成功（エラーなし、または`--exit-zero`指定時） |
| 1 | 品質チェックでエラーが検出された |
| 2 | 解析エラー（ファイルが読めない、構文エラーなど） |
| 3 | チェッカーエラー（内部エラー） |
| 4 | 設定エラー（無効な設定ファイルなど） |

## 環境変数

CLIオプションは環境変数でも設定できます：

| 環境変数 | 対応オプション | 例 |
|----------|----------------|-----|
| `PYTESTEE_CONFIG` | `--config` | `export PYTESTEE_CONFIG="/path/to/config.toml"` |
| `PYTESTEE_FORMAT` | `--format` | `export PYTESTEE_FORMAT="json"` |
| `PYTESTEE_VERBOSE` | `--verbose` | `export PYTESTEE_VERBOSE="true"` |
| `PYTESTEE_SELECT` | `--select` | `export PYTESTEE_SELECT="PTCM,PTAS"` |
| `PYTESTEE_IGNORE` | `--ignore` | `export PYTESTEE_IGNORE="PTST002"` |
| `PYTESTEE_MAX_ASSERTS` | `--max-asserts` | `export PYTESTEE_MAX_ASSERTS="5"` |
| `PYTESTEE_MIN_ASSERTS` | `--min-asserts` | `export PYTESTEE_MIN_ASSERTS="1"` |
| `PYTESTEE_NO_COLOR` | `--no-color` | `export PYTESTEE_NO_COLOR="true"` |

## 使用例

### 基本的な使用

```bash
# カレントディレクトリをチェック
pytestee

# 特定のディレクトリをチェック
pytestee tests/

# 複数のパスをチェック
pytestee tests/unit/ tests/integration/
```

### 出力フォーマット

```bash
# JSON形式で出力
pytestee tests/ --format json

# JSON形式で出力し、ファイルに保存
pytestee tests/ --format json > quality-report.json
```

### ルール選択

```bash
# アサーション関連のルールのみ実行
pytestee tests/ --select PTAS

# 特定のルールのみ実行
pytestee tests/ --select PTAS004,PTCM001

# パターン警告を除外
pytestee tests/ --ignore PTST002
```

### 設定カスタマイズ

```bash
# カスタム設定ファイルを使用
pytestee tests/ --config .pytestee.toml

# しきい値を調整
pytestee tests/ --max-asserts 5 --min-asserts 2
```

### CI/CD での使用

```bash
# CI環境での実行（詳細出力、統計表示）
pytestee tests/ --verbose --show-stats --format json

# エラーがあっても継続（警告のみ）
pytestee tests/ --exit-zero
```

### パイプライン処理

```bash
# 結果をjqで処理
pytestee tests/ --format json | jq '.summary'

# エラーのみ抽出
pytestee tests/ --format json | jq '.files[].results[] | select(.severity == "error")'

# ファイル別サマリー
pytestee tests/ --format json | jq '.files[] | {path: .path, issues: (.results | length)}'
```