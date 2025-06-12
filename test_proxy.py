#!/usr/bin/env python3
"""
Google Sheets検索機能のプロキシ対応テストスクリプト
"""

from google_sheets_handler_proxy import search_in_target_spreadsheet_proxy


def test_proxy_search():
    """
    Google Sheets検索機能をテスト（プロキシ対応版）
    """
    print("Google Sheets検索機能のテスト（プロキシ対応版）を開始します...")
    
    # プロキシ設定の例（必要に応じて変更）
    # proxy_info = {'host': 'proxy.company.com', 'port': 8080}
    proxy_info = None  # 環境変数から自動取得
    
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
            result = search_in_target_spreadsheet_proxy(keyword, proxy_info)
            print(f"結果: {result}")
        except Exception as e:
            print(f"エラー: {e}")


if __name__ == "__main__":
    test_proxy_search()
