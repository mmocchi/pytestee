# list-rules コマンド

利用可能なルール一覧を表示します。各ルールの説明、デフォルト重要度、カテゴリなどの情報を確認できます。

## 基本構文

```bash
pytestee list-rules [OPTIONS]
```

## オプション

### --format, -f
出力フォーマットを指定します。

**値**: `console` | `json`  
**デフォルト**: `console`

=== "console形式"
    ```bash
    pytestee list-rules
    ```

=== "JSON形式"
    ```bash
    pytestee list-rules --format json
    ```

### --category, -c
特定のカテゴリのルールのみ表示します。

**値**: ルールカテゴリ（PTCM, PTST, PTLG, PTAS, PTNM, PTVL, PTEC）

```bash
# アサーション関連ルールのみ表示
pytestee list-rules --category PTAS

# コメントパターンルールのみ表示
pytestee list-rules --category PTCM
```

## 出力例

### console形式

```
Available Rules:
================

PTCM: Comment-Based Pattern Rules
----------------------------------
PTCM001 [ERROR] - AAA Pattern Detected in Comments
  Description: コメント解析によってAAA（Arrange, Act, Assert）パターンが検出された場合
  
PTCM002 [ERROR] - GWT Pattern Detected in Comments
  Description: コメント解析によってGWT（Given, When, Then）パターンが検出された場合

PTST: Structural Pattern Rules
-------------------------------
PTST001 [ERROR] - AAA Pattern Detected Through Structural Separation
  Description: コードセクションを分離する空行によってAAAパターンが検出された場合
  
PTST002 [ERROR] - AAA/GWT Pattern Not Clearly Detected
  Description: 明確なパターン構造が見つからない場合、テスト構成の改善を検討

PTAS: Assertion Rules
---------------------
PTAS001 [ERROR] - Too Few Assertions
  Description: テスト関数のアサーション数が推奨される最小値より少ない場合
  Settings: min_asserts (default: 1)
  
PTAS002 [ERROR] - Too Many Assertions
  Description: テスト関数のアサーション数が推奨される最大値より多い場合
  Settings: max_asserts (default: 3)
  
PTAS004 [ERROR] - No Assertions Found
  Description: テスト関数にアサーションが全く含まれていない場合
  
PTAS005 [ERROR] - Assertion Count OK
  Description: テスト関数が適切な数のアサーションを持っている場合

Total: 15 rules across 7 categories
```

### JSON形式

```json
{
  "categories": {
    "PTCM": {
      "name": "Comment-Based Pattern Rules",
      "rules": [
        {
          "id": "PTCM001",
          "name": "AAA Pattern Detected in Comments",
          "description": "コメント解析によってAAA（Arrange, Act, Assert）パターンが検出された場合",
          "default_severity": "error",
          "settings": []
        },
        {
          "id": "PTCM002",
          "name": "GWT Pattern Detected in Comments",
          "description": "コメント解析によってGWT（Given, When, Then）パターンが検出された場合",
          "default_severity": "error",
          "settings": []
        }
      ]
    },
    "PTAS": {
      "name": "Assertion Rules",
      "rules": [
        {
          "id": "PTAS001",
          "name": "Too Few Assertions",
          "description": "テスト関数のアサーション数が推奨される最小値より少ない場合",
          "default_severity": "error",
          "settings": [
            {
              "name": "min_asserts",
              "type": "int",
              "default": 1,
              "description": "最小アサーション数"
            }
          ]
        }
      ]
    }
  },
  "summary": {
    "total_rules": 15,
    "total_categories": 7
  }
}
```

## カテゴリ別表示

### アサーション関連ルール

```bash
pytestee list-rules --category PTAS
```

```
PTAS: Assertion Rules
=====================

PTAS001 [ERROR] - Too Few Assertions
  Description: テスト関数のアサーション数が推奨される最小値より少ない場合
  Settings: min_asserts (default: 1)

PTAS002 [ERROR] - Too Many Assertions  
  Description: テスト関数のアサーション数が推奨される最大値より多い場合
  Settings: max_asserts (default: 3)

PTAS003 [ERROR] - High Assertion Density
  Description: コード行数に対するアサーションの割合が高い場合
  Settings: max_density (default: 0.5)

PTAS004 [ERROR] - No Assertions Found
  Description: テスト関数にアサーションが全く含まれていない場合

PTAS005 [ERROR] - Assertion Count OK
  Description: テスト関数が適切な数のアサーションを持っている場合

Total: 5 rules in PTAS category
```

### 脆弱性検出ルール

```bash
pytestee list-rules --category PTVL
```

```
PTVL: Vulnerability Detection Rules
===================================

PTVL001 [ERROR] - Private Attribute/Method Access Detection
  Description: テスト関数がプライベート属性やメソッドにアクセスしている場合

PTVL002 [ERROR] - Time Dependency Detection
  Description: テスト関数が時間に依存するコードを含んでいる場合

PTVL003 [ERROR] - Random Dependency Detection
  Description: テスト関数がランダム性に依存するコードを含んでいる場合

PTVL004 [ERROR] - Global State Modification Detection
  Description: テスト関数がグローバル変数を変更している場合

PTVL005 [ERROR] - Class Variable Manipulation Detection
  Description: テストクラス内でクラス変数を操作している場合

Total: 5 rules in PTVL category
```

## 使用例

### 基本的な使用

```bash
# 全ルールを表示
pytestee list-rules

# 特定カテゴリのルールを表示
pytestee list-rules --category PTAS

# JSON形式で全ルールを表示
pytestee list-rules --format json
```

### 情報収集とフィルタリング

```bash
# アサーション関連ルールをJSONで取得
pytestee list-rules --category PTAS --format json

# ルール一覧をファイルに保存
pytestee list-rules --format json > rules-reference.json

# 特定の情報を抽出（jqが必要）
pytestee list-rules --format json | jq '.categories.PTAS.rules[].id'
```

### 設定検討時の活用

```bash
# エッジケースルールの詳細を確認
pytestee list-rules --category PTEC

# 設定可能なパラメータがあるルールを確認
pytestee list-rules --format json | jq '.categories[].rules[] | select(.settings | length > 0)'

# デフォルト重要度がerrorでないルールを確認  
pytestee list-rules --format json | jq '.categories[].rules[] | select(.default_severity != "error")'
```

## ルールカテゴリ一覧

| カテゴリ | 名前 | 説明 |
|----------|------|------|
| **PTCM** | Comment-Based Pattern | コメントによるパターン検出 |
| **PTST** | Structural Pattern | 構造的パターン検出 |
| **PTLG** | Logical Pattern | 論理的フローパターン検出 |
| **PTAS** | Assertion Rules | アサーション関連ルール |
| **PTNM** | Naming Rules | 命名規則 |
| **PTVL** | Vulnerability Detection | 脆弱性検出 |
| **PTEC** | Edge Case Coverage | エッジケース網羅性 |

## 活用シーン

### 新しいプロジェクトの設定時

```bash
# 利用可能なルールを確認
pytestee list-rules

# 重要なルールを特定
pytestee list-rules --category PTAS
pytestee list-rules --category PTVL

# 設定ファイル作成の参考にする
pytestee list-rules --format json > rules-info.json
```

### CI/CD設定の検討

```bash
# CI用の軽量ルールセットを検討
pytestee list-rules --category PTAS

# 開発段階で有効にするルールを検討
pytestee list-rules --category PTCM
pytestee list-rules --category PTST
```

### チーム内でのルール説明

```bash
# チームメンバーにルール説明用の資料を作成
pytestee list-rules > team-rules-reference.txt

# 特定カテゴリの詳細をチーム内で共有
pytestee list-rules --category PTEC --format json
```