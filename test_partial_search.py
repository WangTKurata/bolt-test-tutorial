#!/usr/bin/env python3
"""
Google Sheets部分一致検索機能のテストスクリプト（4行目以降のみ）
"""

from google_sheets_handler_advanced import advanced_search_in_target_spreadsheet


def test_partial_search_only():
    """
    Google Sheets部分一致検索機能をテスト（4行目以降のみ）
    """
    print("=== Google Sheets部分一致検索機能のテスト（4行目以降のみ） ===\n")
    
    # テスト用の検索キーワード
    test_cases = [
        'フリーソフト',
        'software',
        'Slack',
        'ソフト',
        'Windows',
        '存在しないキーワード12345'
    ]
    
    for i, keyword in enumerate(test_cases, 1):
        print(f"テスト {i}: '{keyword}'")
        print("-" * 50)
        
        try:
            # 部分一致検索のみを実行
            result = advanced_search_in_target_spreadsheet(keyword, search_types=['partial'])
            
            print(f"結果: {result['message']}")
            
            if result['found'] and result['matches']:
                print(f"マッチ件数: {len(result['matches'])}")
                print("\n上位の結果:")
                
                for j, match in enumerate(result['matches'][:5], 1):  # 上位5件まで表示
                    print(f"  {j}. {match['text'][:80]}{'...' if len(match['text']) > 80 else ''}")
                    print(f"     位置: {match['position']}")
            
        except Exception as e:
            print(f"エラー: {e}")
        
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    test_partial_search_only()
