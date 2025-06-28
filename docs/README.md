# Pytestee Documentation

Pytesteeは、pytest形式のテストコードの品質を向上させるためのCLIツールです。Clean Architectureの原則に基づいて構築され、ルールベースのアプローチでテストの品質を評価します。

## ドキュメント一覧

### はじめに
- **[Getting Started](getting-started.md)** - インストールと基本的な使用方法
- **[Configuration](configuration.md)** - 詳細な設定ガイド
- **[Rules Reference](rules.md)** - 全ルールの詳細なリファレンス

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
```bash
# テストファイルをチェック
pytestee tests/

# JSON形式で出力
pytestee tests/ --format json

# 特定のルールのみ実行
pytestee tests/ --select PTCM,PTAS
```

### 設定例
```toml
[tool.pytestee]
select = ["PTCM", "PTAS", "PTEC"]
ignore = ["PTST002"]

[tool.pytestee.severity]
PTCM001 = "info"      # AAA パターン検出
PTAS004 = "error"     # アサーションなし
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

## コントリビューション

### 新しいルールの追加
1. 適切なカテゴリを選択または作成
2. `infrastructure/rules/` に実装
3. テストケースを追加
4. ドキュメントを更新

### 開発環境のセットアップ
```bash
# 依存関係のインストール
uv sync

# 全チェックの実行
task check

# テストの実行
task test
```

## リソース

- **[GitHub Repository](https://github.com/mmocchi/pytestee)**
- **[Issue Tracker](https://github.com/mmocchi/pytestee/issues)**
- **[PyPI Package](https://pypi.org/project/pytestee/)**

## ライセンス

MIT License - 詳細は [LICENSE](../LICENSE) ファイルを参照してください。