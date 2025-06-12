#!/usr/bin/env python3
"""
ソフトウェア調査機能のテストスクリプト
"""

import os

from software_research import research_and_suggest_software


def test_software_research():
    """
    ソフトウェア調査機能をテスト
    """
    print("=== ソフトウェア調査機能のテスト ===\n")
    
    # OpenAI API キーの確認
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY環境変数が設定されていません")
        print("以下のコマンドで設定してください:")
        print('$env:OPENAI_API_KEY="your-api-key-here"')
        return
    
    print(f"✅ OpenAI API キーが設定されています: {api_key[:10]}...")
    
    # テスト用のソフトウェア名
    test_software_list = [
        "Visual Studio Code",
        "Docker Desktop",
        "存在しないソフトウェア12345"
    ]
    
    for i, software_name in enumerate(test_software_list, 1):
        print(f"\nテスト {i}: '{software_name}'")
        print("-" * 50)
        
        try:
            result = research_and_suggest_software(software_name)
            
            print(f"ソフトウェア名: {result['software_name']}")
            
            if result['research']:
                research_info = result['research']
                print(f"📋 カテゴリ: {research_info.get('category', '不明')}")
                print(f"🌐 ダウンロードページ: {research_info.get('download_page', '不明')}")
                print(f"💻 プラットフォーム: {research_info.get('platform', '不明')}")
                print(f"🏢 商用利用: {research_info.get('free_commercial', '不明')}")
                print(f"📝 備考: {research_info.get('remarks', '承認待ち')}")
                print(f"⚠️ 特記事項: {research_info.get('special_remarks', '不明')}")
            else:
                print("❌ 調査結果を取得できませんでした")
            
            # 追加提案の結果
            add_suggestion = result['add_suggestion']
            if add_suggestion['success']:
                print("\n✅ リスト追加提案: 成功")
                print(f"メッセージ: {add_suggestion['message']}")
                if add_suggestion.get('data'):
                    print(f"追加予定データ: {add_suggestion['data']}")
            else:
                print(f"\n❌ リスト追加提案: 失敗")
                print(f"メッセージ: {add_suggestion['message']}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    test_software_research()
