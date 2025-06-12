import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from google_sheets_handler_advanced import advanced_search_in_target_spreadsheet

# ボットトークンを渡してアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'こんにちは' を含むメッセージをリッスンします
@app.message("こんにちは")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"こんにちは、<@{message['user']}> さん！"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "クリックしてください"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"こんにちは、<@{message['user']}> さん！",
    )

@app.action("button_click")
def action_button_click(body, ack, say):
    # アクションを確認したことを即時で応答します
    ack()
    # チャンネルにメッセージを投稿します
    say(f"<@{body['user']['id']}> さんがボタンをクリックしました！")

# 一般的なメッセージイベントを処理（未処理のイベントを防ぐため）
@app.event("message")
def handle_message_events(body, logger):
    # 一般的なメッセージは特に処理しない（ログのみ）
    logger.info("メッセージイベントを受信しました")

# Botがメンションされたときの処理
@app.event("app_mention")
def handle_app_mention(event, say):
    try:
        # メンションされたメッセージからテキストを抽出
        text = event.get('text', '')
        
        # ボットのメンションを除去してクリーンなテキストを取得
        # <@U...> の形式のメンションを除去
        clean_text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
        
        if clean_text:
            # Google Spreadsheetで部分一致検索を実行（4行目以降のみ）
            result = advanced_search_in_target_spreadsheet(clean_text, search_types=['partial'])
            
            if result['found']:
                # 検索結果が見つかった場合
                response = f"「{clean_text}」の検索結果:\n{result['message']}\n\n"
                
                # 上位3件の結果を表示
                for i, match in enumerate(result['matches'][:3], 1):
                    response += f"{i}. {match['text'][:100]}{'...' if len(match['text']) > 100 else ''}\n"
                    response += f"   位置: {match['position']}\n\n"
                
                say(response)
            else:
                # 検索結果が見つからなかった場合
                say(f"「{clean_text}」は見つかりませんでした")
        else:
            # テキストが空の場合は従来の応答
            say("ふむふむ")
            
    except Exception as e:
        print(f"メンション処理エラー: {e}")
        say("検索中にエラーが発生しました")

if __name__ == "__main__":
    # アプリを起動して、ソケットモードで Slack に接続します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
