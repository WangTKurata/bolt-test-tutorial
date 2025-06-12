# bolt-test-tutorial

Slack BotとGoogle Sheets連携アプリケーション

## 機能

1. **基本的なSlack Bot機能**
   - 「こんにちは」メッセージへの応答
   - ボタンクリックイベントの処理

2. **Google Sheets部分一致検索機能**
   - ボットにメンションすると、指定されたGoogle Spreadsheetでテキストを検索
   - 検索対象: "I want to use free software / フリーソフトを利用したい のコピー"
   - **検索範囲**: 4行目以降の1列目のみ（ヘッダー行を除外）
   - **検索タイプ**: 部分一致検索のみ
     - 入力したテキストを含むセルを検索
     - 大文字小文字は区別しません
   - 検索結果には位置情報を表示
   - 上位3件の結果を詳細表示

3. **ソフトウェア調査機能（ChatGPT API連携）**
   - 検索で見つからなかった場合、ChatGPT APIを使用してソフトウェア情報を自動調査
   - **調査項目**:
     - カテゴリ（ソフトウェアの種類）
     - 公式ダウンロードページ
     - 対応プラットフォーム（OS）
     - セキュリティ上の注意点
     - 企業での無料利用可否
     - その他特記事項
   - 調査結果をスプレッドシートへの追加提案として提示
   - Remarks列に「承認待ち」として記録
   - 最終的な承認は人間が判断

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
```powershell
$env:SLACK_BOT_TOKEN="xoxb-XXXXX"
$env:SLACK_APP_TOKEN="xapp-YYYYY"
$env:OPENAI_API_KEY="sk-ZZZZZ"
$env:GOOGLE_CREDENTIALS_PATH="google_service_account.json"
```

### 3. Google Sheets API認証
- Google Cloud Platformのサービスアカウント認証情報JSONファイルが必要です
- デフォルトファイル名: `google_service_account.json`
- 環境変数 `GOOGLE_CREDENTIALS_PATH` で別のパスを指定可能
- このサービスアカウントは対象のGoogle Spreadsheetへのアクセス権限が必要です

#### セキュリティ上の注意
- 認証情報ファイルは `.gitignore` に追加してGitHubにコミットしないでください
- ファイル名は汎用的な名称を使用し、プロジェクト固有の情報を含めないでください

### 4. OpenAI API設定
- OpenAI APIキーが必要です
- ソフトウェア調査機能で使用されます
- 環境変数 `OPENAI_API_KEY` に設定してください

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

- `app.py`: メインのSlack Botアプリケーション（高度な検索機能統合済み）
- `google_sheets_handler.py`: Google Sheets操作を担当するモジュール（基本版）
- `google_sheets_handler_proxy.py`: Google Sheets操作を担当するモジュール（プロキシ対応版）
- `google_sheets_handler_advanced.py`: Google Sheets操作を担当するモジュール（高度な検索機能付き）
- `test_sheets.py`: Google Sheets検索機能のテストスクリプト（基本版）
- `test_proxy.py`: Google Sheets検索機能のテストスクリプト（プロキシ対応版）
- `test_advanced_search.py`: 高度な検索機能のテストスクリプト
- `debug_test.py`: 詳細なデバッグ情報付きテストスクリプト
- `requirements.txt`: 依存関係の定義
- `.vscode/boltslacktest-wang-40b68186e2db.json`: Google Sheets APIの認証情報

## 高度な検索機能

### 検索タイプの詳細

1. **完全一致検索 (exact)**
   - 入力したテキストと完全に一致するセルを検索
   - 大文字小文字は区別しません
   - スコア: 100

2. **部分一致検索 (partial)**
   - 入力したテキストを含むセルを検索
   - 「フリー」で検索すると「フリーソフト」も見つかります
   - スコア: 90

3. **あいまい検索 (fuzzy)**
   - 類似度を使用して関連するテキストを検索
   - タイプミスや表記ゆれにも対応
   - スコア: 70-100（類似度による）

### テスト実行

```bash
# 高度な検索機能のテスト
python test_advanced_search.py

# 基本検索機能のテスト
python test_sheets.py

# プロキシ対応版のテスト
python test_proxy.py
```

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

ボットが応答（部分一致検索、4行目以降のみ）：
```
「フリーソフト」の検索結果:
'フリーソフト'の検索結果: 3件見つかりました

1. ・フリーソフトウェアの利用申請は、Slack チャンネル #a-software にて受け付けます。
   位置: 行5, 列1

2. ・利用を許可した場合、該当のフリーソフトウェアを OKリスト に追加してください。
   位置: 行6, 列1

3. ・利用を許可できない場合、該当のフリーソフトウェアを NGリスト に記載してください。
   位置: 行7, 列1
```

### その他の検索例

```
@bot Slack
```
→ 部分一致検索で「Slack」を含むテキストを検索（4行目以降のみ）

```
@bot ソフト
```
→ 部分一致検索で「ソフト」を含むテキストを検索（4行目以降のみ）

### ソフトウェア調査機能の使用例

検索で見つからないソフトウェアをメンションした場合：
```
@bot Visual Studio Code
```

ボットが応答（ソフトウェア調査結果）：
```
「Visual Studio Code」は見つかりませんでした。調査を開始します...

「Visual Studio Code」の調査結果:

📋 カテゴリ: コードエディタ・統合開発環境
🌐 ダウンロードページ: https://code.visualstudio.com/
💻 プラットフォーム: Windows, Mac, Linux
🏢 商用利用: 可能（無料）
📝 備考: 承認待ち - Microsoft製の軽量で高機能なコードエディタ
⚠️ 特記事項: オープンソース、豊富な拡張機能

✅ この情報をリストに追加することを提案します。
管理者による最終承認が必要です。
```

### テスト実行

```bash
# 部分一致検索のテスト（4行目以降のみ）
python test_partial_search.py

# ソフトウェア調査機能のテスト
python test_software_research.py
```

### ファイル構成（追加）

- `software_research.py`: ソフトウェア調査機能を担当するモジュール（ChatGPT API連携）
- `test_software_research.py`: ソフトウェア調査機能のテストスクリプト
