#!/usr/bin/env python3
"""
Google Sheets検索機能のテストスクリプト
"""

from google_sheets_handler import search_in_target_spreadsheet


def test_search():
    """
    Google Sheets検索機能をテスト
    """
    print("Google Sheets検索機能のテストを開始します...")
    
    # テスト用の検索キーワード
    test_keywords = [
        "フリーソフト",
        "software",
        "存在しないキーワード12345",
        "利用"
    ]
    
    for keyword in test_keywords:
        print(f"\n検索キーワード: '{keyword}'")
        try:
            result = search_in_target_spreadsheet(keyword)
            print(f"結果: {result}")
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_search()
