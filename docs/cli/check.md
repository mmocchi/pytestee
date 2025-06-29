# check コマンド

テストファイルの品質をチェックします。これがデフォルトのコマンドなので、省略可能です。

## 基本構文

```bash
pytestee check [OPTIONS] [PATHS...]
pytestee [OPTIONS] [PATHS...]  # checkは省略可能
```

## オプション

### --format, -f
出力フォーマットを指定します。

**値**: `console` | `json`  
**デフォルト**: `console`

```bash
# コンソール形式（デフォルト）
pytestee tests/ --format console

# JSON形式
pytestee tests/ --format json
```

#### 出力例

=== "console形式"
    ```
    tests/test_example.py:15:5: PTAS004 [ERROR] No assertions found in test function
    tests/test_example.py:25:5: PTCM001 [INFO] AAA pattern detected in comments
    ```

=== "JSON形式"
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

### --config, -c
設定ファイルのパスを指定します。

**デフォルト**: 自動検索（`pyproject.toml`, `.pytestee.toml`, `setup.cfg`）

```bash
pytestee tests/ --config custom-config.toml
pytestee tests/ -c .pytestee.toml
```

### --select
実行するルールを明示的に指定します。

**値**: ルールID、カテゴリ、またはカンマ区切りのリスト

=== "特定のルール"
    ```bash
    pytestee tests/ --select PTAS004
    ```

=== "カテゴリ全体"
    ```bash
    pytestee tests/ --select PTCM,PTAS
    ```

=== "複数ルール"
    ```bash
    pytestee tests/ --select PTCM001,PTAS001,PTAS004
    ```

### --ignore
除外するルールを指定します。

**値**: ルールID、カテゴリ、またはカンマ区切りのリスト

=== "特定のルール"
    ```bash
    pytestee tests/ --ignore PTST002
    ```

=== "カテゴリ全体"
    ```bash
    pytestee tests/ --ignore PTEC
    ```

=== "複数ルール"
    ```bash
    pytestee tests/ --ignore PTST002,PTNM001
    ```

### --verbose, -v
詳細な出力を有効にします。複数指定でより詳細になります。

```bash
pytestee tests/ --verbose
pytestee tests/ -v
pytestee tests/ -vv  # より詳細
```

### --quiet, -q
出力を最小限に抑えます。

```bash
pytestee tests/ --quiet
pytestee tests/ -q
```

### --show-stats
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

### --exclude
除外するパスパターンを指定します。

**値**: glob パターンのカンマ区切りリスト

```bash
pytestee tests/ --exclude "tests/legacy/*,**/conftest.py"
```

### --include
含めるパスパターンを指定します。

**値**: glob パターンのカンマ区切りリスト

```bash
pytestee tests/ --include "tests/unit/*,tests/integration/*"
```

### --max-asserts
アサーションの最大数を設定します（PTAS002のしきい値）。

**値**: 正の整数  
**デフォルト**: 3

```bash
pytestee tests/ --max-asserts 5
```

### --min-asserts
アサーションの最小数を設定します（PTAS001のしきい値）。

**値**: 0以上の整数  
**デフォルト**: 1

```bash
pytestee tests/ --min-asserts 2
```

### --no-color
カラー出力を無効にします。

```bash
pytestee tests/ --no-color
```

### --exit-zero
エラーが見つかっても終了コード0で終了します。

```bash
pytestee tests/ --exit-zero
```

## パス引数

チェック対象のファイルまたはディレクトリのパスを指定します。複数指定可能です。

=== "単一ファイル"
    ```bash
    pytestee tests/test_example.py
    ```

=== "ディレクトリ"
    ```bash
    pytestee tests/
    ```

=== "複数パス"
    ```bash
    pytestee tests/unit/ tests/integration/ src/tests/
    ```

**デフォルト**: カレントディレクトリ（`.`）

## 使用例

### 基本的なチェック

```bash
# 現在のディレクトリをチェック
pytestee

# 特定のディレクトリをチェック
pytestee tests/

# 詳細情報付きでチェック
pytestee tests/ --verbose --show-stats
```

### ルールのカスタマイズ

```bash
# アサーション関連のルールのみ実行
pytestee tests/ --select PTAS

# 特定の問題のあるルールを除外
pytestee tests/ --ignore PTST002,PTNM001

# アサーション数の閾値を調整
pytestee tests/ --max-asserts 5 --min-asserts 2
```

### CI/CD環境での使用

```bash
# エラーのみ出力（CI用）
pytestee tests/ --quiet --format json --exit-zero

# 詳細な統計付きでレポート出力
pytestee tests/ --format json --show-stats > quality-report.json

# 重要なルールのみCI実行
pytestee tests/ --select PTAS004,PTVL --format json
```

### パフォーマンス最適化

```bash
# 特定のファイルのみチェック
pytestee tests/ --include "tests/unit/*"

# レガシーファイルを除外
pytestee tests/ --exclude "tests/legacy/*,tests/fixtures/*"

# 軽量ルールセットでクイックチェック
pytestee tests/ --select PTAS004,PTCM001 --quiet
```