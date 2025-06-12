# bolt-test-tutorial

Slack BotとGoogle Sheets連携アプリケーション

## 機能

1. **基本的なSlack Bot機能**
   - 「こんにちは」メッセージへの応答
   - ボタンクリックイベントの処理

2. **Google Sheets検索機能**
   - ボットにメンションすると、指定されたGoogle Spreadsheetでテキストを検索
   - 検索対象: "I want to use free software / フリーソフトを利用したい のコピー"
   - 結果: 「ありました」または「ありません」で応答

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
```powershell
$env:SLACK_BOT_TOKEN="xoxb-XXXXX"
$env:SLACK_APP_TOKEN="xapp-YYYYY"
```

### 3. Google Sheets API認証
- `.vscode/boltslacktest-wang-40b68186e2db.json` にサービスアカウントの認証情報が格納されています
- このサービスアカウントは対象のGoogle Spreadsheetへのアクセス権限が必要です

### 4. 企業セキュリティソフトウェア（Netskope等）の対応
企業環境でNetskopeなどのセキュリティソフトウェアが通信を阻害する場合：

#### 一時的な対処法：
1. Netskopeクライアントを一時的に無効化
2. 管理者権限でセキュリティソフトを一時停止

#### 恒久的な対処法：
1. **プロキシ設定の追加**（環境変数で設定可能）：
   ```powershell
   $env:HTTP_PROXY="http://proxy.company.com:8080"
   $env:HTTPS_PROXY="http://proxy.company.com:8080"
   ```

2. **IT部門への申請**：
   - Google APIs（googleapis.com）へのアクセス許可申請
   - OAuth2エンドポイント（oauth2.googleapis.com）への許可申請

3. **証明書の追加**：
   - 企業の内部証明書をPythonの証明書ストアに追加

### 4. VSCode設定
.gitignore に .vscode/ を追加しておいて、.vscode/launch.json に書いておくと良い。

```json
"env": {
  "SLACK_BOT_TOKEN": "xoxb-XXXXX",
  "SLACK_APP_TOKEN": "xapp-YYYYY"
}
```

## 使用方法

### アプリケーションの起動
```bash
python app.py
```

### テスト実行
```bash
python test_sheets.py
```

## ファイル構成

- `app.py`: メインのSlack Botアプリケーション
- `google_sheets_handler.py`: Google Sheets操作を担当するモジュール
- `google_sheets_handler_proxy.py`: Google Sheets操作を担当するモジュール（プロキシ対応版）
- `test_sheets.py`: Google Sheets検索機能のテストスクリプト
- `test_proxy.py`: Google Sheets検索機能のテストスクリプト（プロキシ対応版）
- `debug_test.py`: 詳細なデバッグ情報付きテストスクリプト
- `requirements.txt`: 依存関係の定義
- `.vscode/boltslacktest-wang-40b68186e2db.json`: Google Sheets APIの認証情報

## 企業環境での使用

### Netskope等のセキュリティソフトウェア対応

企業環境でセキュリティソフトウェアが通信を阻害する場合は、プロキシ対応版を使用してください：

1. **環境変数でプロキシを設定**：
   ```powershell
   $env:HTTP_PROXY="http://proxy.company.com:8080"
   $env:HTTPS_PROXY="http://proxy.company.com:8080"
   ```

2. **プロキシ対応版のテスト実行**：
   ```bash
   python test_proxy.py
   ```

3. **app.pyでプロキシ対応版を使用する場合**：
   `app.py`の import 文を以下のように変更：
   ```python
   from google_sheets_handler_proxy import search_in_target_spreadsheet_proxy as search_in_target_spreadsheet
   ```

## 使用例

Slackでボットをメンションして検索したいテキストを送信：
```
@bot フリーソフト
```

ボットが応答：
```
「フリーソフト」を検索しました: ありました
```
