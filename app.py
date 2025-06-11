import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

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

# Botがメンションされたときの処理
@app.event("app_mention")
def handle_app_mention(event, say):
    # メンションされたら"ふむふむ"と返す
    say("ふむふむ")

if __name__ == "__main__":
    # アプリを起動して、ソケットモードで Slack に接続します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
