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

## コマンド一覧

- **[check](check.md)** - テストファイルの品質をチェック（デフォルト）
- **[show-config](show-config.md)** - 現在の設定を表示
- **[list-rules](list-rules.md)** - 利用可能なルール一覧を表示

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