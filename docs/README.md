# Pytestee

Pytesteeは、pytest形式のテストコードの品質を向上させるためのCLIツールです。ルールベースのアプローチでテストの品質を評価し、より良いテストコードの作成をサポートします。

!!! info "ドキュメントナビゲーション"
    - 初めての方は **[はじめに](getting-started.md)** からお読みください
    - 詳細な設定は **[設定ガイド](configuration.md)** をご覧ください
    - 全ルールの詳細は **[ルールリファレンス](rules.md)** で確認できます

### 主要機能

Pytesteeは以下の領域でテストの品質をチェックします：

#### 🔍 パターン検出
- **AAA パターン** (Arrange, Act, Assert)
- **GWT パターン** (Given, When, Then)
- コメントベース、構造的、論理的な検出手法

#### ⚡ アサーション分析
- アサーション数の適切性
- アサーション密度の評価
- 不足・過多の検出

#### 🛡️ 脆弱性検出
- プライベートメンバーへのアクセス
- 時間・ランダム性依存の検出
- グローバル状態の変更

#### 🎯 エッジケース網羅性
- 数値・コレクション・文字列のエッジケース
- 正常・異常ケースの比率分析
- 全体的な網羅性スコア

#### 📝 命名規則
- 日本語テストメソッド名の推奨

## クイックスタート

### インストール
```bash
pip install pytestee
```

### 基本的な使用方法

=== "基本チェック"
    ```bash
    # テストファイルをチェック
    pytestee tests/
    ```

=== "JSON出力"
    ```bash
    # JSON形式で出力
    pytestee tests/ --format json
    ```

=== "ルール選択"
    ```bash
    # 特定のルールのみ実行
    pytestee tests/ --select PTCM,PTAS
    ```

### 設定例

=== "基本設定"
    ```toml
    [tool.pytestee]
    select = ["PTCM", "PTAS"]
    
    [tool.pytestee.severity]
    PTCM001 = "info"      # AAA パターン検出
    PTAS004 = "error"     # アサーションなし
    ```

=== "厳格設定"
    ```toml
    [tool.pytestee]
    select = ["PT"]  # すべてのルール
    max_asserts = 3
    min_asserts = 1
    
    [tool.pytestee.severity]
    "PTAS" = "error"
    "PTVL" = "error"
    ```

## ルール体系

Pytesteeは以下のカテゴリでルールを組織化しています：

| カテゴリ | 説明 | 例 |
|---------|------|----| 
| **PTCM** | コメントベースパターン | AAA/GWT コメントの検出 |
| **PTST** | 構造的パターン | 空行による構造分離 |
| **PTLG** | 論理的パターン | AST解析によるパターン検出 |
| **PTAS** | アサーション | 数・密度・適切性の評価 |
| **PTNM** | 命名規則 | 日本語メソッド名の推奨 |
| **PTVL** | 脆弱性検出 | 依存性・状態変更の検出 |
| **PTEC** | エッジケース | 網羅性とバランスの分析 |

## アーキテクチャ

Pytesteeは以下のClean Architectureレイヤーで構成されています：

```
src/pytestee/
├── domain/          # ビジネスロジック
├── usecases/        # アプリケーションロジック
├── adapters/        # 外部インターフェース
│   ├── cli/         # CLIコマンド
│   ├── presenters/  # 出力フォーマット
│   └── repositories/ # ファイルシステム
├── infrastructure/ # 具象実装
│   ├── checkers/   # 品質チェッカー
│   ├── rules/      # ルール実装
│   ├── config/     # 設定管理
│   └── ast_parser.py # AST解析
└── registry.py     # 依存性注入
```

## 良いテストの例

!!! example "推奨されるテストパターン"
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

    このテストは以下の点で優れています：
    
    - ✓ **日本語メソッド名** で可読性が高い
    - ✓ **AAAパターン** で構造が明確
    - ✓ **適切なアサーション数** で検証が十分

## リソース

- **[GitHub Repository](https://github.com/mmocchi/pytestee)**
- **[Issue Tracker](https://github.com/mmocchi/pytestee/issues)**
- **[PyPI Package](https://pypi.org/project/pytestee/)**

