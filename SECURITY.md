# セキュリティポリシー

## 脆弱性の報告

セキュリティ上の問題を見つけた場合は、**公開 Issue を立てず**、GitHub の
**Private Vulnerability Reporting** から非公開でご報告ください。

- このリポジトリの **Security** タブ → **Report a vulnerability** から送信できます。
- 連絡先メールアドレスは公開していません。上記の GitHub 機能をご利用ください。

## このプロジェクトのセキュリティ対策

- 依存関係: **Dependabot** による脆弱性アラート + 自動修正 PR
- GitHub Actions: action を full commit SHA に固定・最小権限・**zizmor** による静的監査
- 秘密情報: **gitleaks** によるコミット時検査(混入を防止)
- 姿勢スコア: **OpenSSF Scorecard** を週次で実行
