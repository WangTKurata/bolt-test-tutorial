import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from google_sheets_handler_advanced import advanced_search_in_target_spreadsheet
from software_research import research_and_suggest_software

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
                # 検索結果が見つからなかった場合、ソフトウェア調査を実行
                say(f"「{clean_text}」は見つかりませんでした。調査を開始します...")
                
                try:
                    # ChatGPT APIを使用してソフトウェア情報を調査
                    research_result = research_and_suggest_software(clean_text)
                    
                    if research_result['research']:
                        # 調査結果を整形して表示
                        research_info = research_result['research']
                        response = f"「{clean_text}」の調査結果:\n\n"
                        response += f"📋 カテゴリ: {research_info.get('category', '不明')}\n"
                        response += f"🌐 ダウンロードページ: {research_info.get('download_page', '不明')}\n"
                        response += f"💻 プラットフォーム: {research_info.get('platform', '不明')}\n"
                        response += f"🏢 商用利用: {research_info.get('free_commercial', '不明')}\n"
                        response += f"📝 備考: {research_info.get('remarks', '承認待ち')}\n"
                        response += f"⚠️ 特記事項: {research_info.get('special_remarks', '不明')}\n\n"
                        
                        # 追加提案の結果
                        add_suggestion = research_result['add_suggestion']
                        if add_suggestion['success']:
                            response += "✅ この情報をリストに追加することを提案します。\n"
                            response += "管理者による最終承認が必要です。"
                        else:
                            response += f"❌ リスト追加提案でエラーが発生しました: {add_suggestion['message']}"
                        
                        say(response)
                    else:
                        say(f"「{clean_text}」の調査中にエラーが発生しました。")
                        
                except Exception as research_error:
                    print(f"ソフトウェア調査エラー: {research_error}")
                    say(f"「{clean_text}」の調査中にエラーが発生しました。")
        else:
            # テキストが空の場合は従来の応答
            say("ふむふむ")
            
    except Exception as e:
        print(f"メンション処理エラー: {e}")
        say("検索中にエラーが発生しました")

if __name__ == "__main__":
    # アプリを起動して、ソケットモードで Slack に接続します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
