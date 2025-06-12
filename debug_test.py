#!/usr/bin/env python3
"""
Google Sheets検索機能のデバッグテストスクリプト
"""

import sys
import traceback

from google_sheets_handler import GoogleSheetsHandler


def debug_test():
    """
    Google Sheets検索機能をデバッグテスト
    """
    print("=== Google Sheets検索機能のデバッグテストを開始 ===")
    
    try:
        # 認証情報ファイルのパス
        credentials_path = ".vscode/boltslacktest-wang-40b68186e2db.json"
        print(f"認証情報ファイル: {credentials_path}")
        
        # 検索対象のスプレッドシート名
        target_spreadsheet = "I want to use free software / フリーソフトを利用したい のコピー"
        print(f"対象スプレッドシート: {target_spreadsheet}")
        
        # Google Sheetsハンドラーを初期化
        print("Google Sheetsハンドラーを初期化中...")
        sheets_handler = GoogleSheetsHandler(credentials_path)
        print("初期化完了")
        
        # スプレッドシートを検索
        print("スプレッドシートを検索中...")
        spreadsheet_id = sheets_handler.find_spreadsheet_by_name(target_spreadsheet)
        
        if spreadsheet_id:
            print(f"スプレッドシートが見つかりました: {spreadsheet_id}")
            
            # データを取得してみる
            print("データを取得中...")
            all_data = sheets_handler.get_all_sheet_data(spreadsheet_id)
            print(f"取得したデータ行数: {len(all_data)}")
            
            # 最初の数行を表示
            if all_data:
                print("最初の3行のデータ:")
                for i, row in enumerate(all_data[:3]):
                    print(f"  行{i+1}: {row}")
            
            # テスト検索
            test_keyword = "フリーソフト"
            print(f"\n'{test_keyword}'を検索中...")
            found = sheets_handler.search_text_in_spreadsheet(target_spreadsheet, test_keyword)
            print(f"検索結果: {'見つかりました' if found else '見つかりませんでした'}")
            
        else:
            print("スプレッドシートが見つかりませんでした")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("詳細なエラー情報:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_test()
