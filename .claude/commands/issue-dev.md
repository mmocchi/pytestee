---
allowed_tools: Bash(git:*), Bash(gh:*), Bash(task:*), Read(*.md), Read(*.py), Read(*.toml), Fetch(*)
description: "引数で指定したissueの内容に従って開発を行う"
---

あなたは経験豊かなソフトウェアエンジニアです。
あなたは、引数で指定したissueの内容に従って開発を行います。
あなたは、以下のコマンドを使用して開発を行います。

## 使用する主なコマンド

- git: gitの操作を行う
- gh: GitHubの操作を行う
- task: taskの操作を行う

## 開発の流れ

1. 引数で指定したissueの内容をgh issue view {issue_number}で読み込む
2. issueの内容にしたがって、mainブランチから新しいブランチを作成する。このとき、ブランチ名は `feature/{issue_number}_{開発する内容の概要を英語で}`
3. 新しいブランチで開発を行う
4. 開発が終わったら、task checkを実行して、エラーがないか確認する。エラーがあればエラーがなくなるまで修正する
5. task checkで問題がなくなったらコミットして、pushする
6. gh pr コマンドを使ってPull Requestを作成する。Pull Requestは日本語で作成してください。
7. CIがパスするのを確認して、パスしていなかったら問題を修正する
