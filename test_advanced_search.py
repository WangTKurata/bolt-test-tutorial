#!/usr/bin/env python3
"""
Google Sheets高度な検索機能のテストスクリプト
"""

from google_sheets_handler_advanced import advanced_search_in_target_spreadsheet


def test_advanced_search():
    """
    Google Sheets高度な検索機能をテスト
    """
    print("=== Google Sheets高度な検索機能のテストを開始 ===\n")
    
    # テスト用の検索キーワード
    test_cases = [
        {
            'keyword': 'フリーソフト',
            'types': ['exact', 'partial', 'fuzzy'],
            'description': '完全一致・部分一致・あいまい検索'
        },
        {
            'keyword': 'software',
            'types': ['partial'],
            'description': '部分一致検索のみ'
        },
        {
            'keyword': 'ソフトウェア',
            'types': ['fuzzy'],
            'description': 'あいまい検索のみ'
        },
        {
            'keyword': 'フリー',
            'types': ['partial', 'fuzzy'],
            'description': '部分一致・あいまい検索'
        },
        {
            'keyword': 'Slack',
            'types': ['exact', 'partial', 'fuzzy'],
            'description': '全検索タイプ'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        keyword = test_case['keyword']
        search_types = test_case['types']
        description = test_case['description']
        
        print(f"テスト {i}: '{keyword}' ({description})")
        print(f"検索タイプ: {', '.join(search_types)}")
        print("-" * 50)
        
        try:
            result = advanced_search_in_target_spreadsheet(keyword, search_types)
            
            print(f"結果: {result['message']}")
            
            if result['found'] and result['matches']:
                print(f"マッチ件数: {len(result['matches'])}")
                print("\n上位の結果:")
                
                for j, match in enumerate(result['matches'][:5], 1):  # 上位5件まで表示
                    print(f"  {j}. [{match['type']}] {match['text'][:50]}{'...' if len(match['text']) > 50 else ''}")
                    print(f"     位置: {match['position']}, スコア: {match['score']}")
            
        except Exception as e:
            print(f"エラー: {e}")
        
        print("\n" + "=" * 60 + "\n")


def test_specific_search_types():
    """
    特定の検索タイプの詳細テスト
    """
    print("=== 検索タイプ別詳細テスト ===\n")
    
    keyword = "ソフト"
    
    # 各検索タイプを個別にテスト
    search_types_list = [
        (['exact'], '完全一致検索'),
        (['partial'], '部分一致検索'),
        (['fuzzy'], 'あいまい検索')
    ]
    
    for search_types, description in search_types_list:
        print(f"{description}: '{keyword}'")
        print("-" * 30)
        
        try:
            result = advanced_search_in_target_spreadsheet(keyword, search_types)
            
            print(f"結果: {result['message']}")
            
            if result['found'] and result['matches']:
                for match in result['matches'][:3]:  # 上位3件
                    print(f"  [{match['type']}] {match['text'][:40]}{'...' if len(match['text']) > 40 else ''}")
                    print(f"  スコア: {match['score']}, 位置: {match['position']}")
                    print()
            
        except Exception as e:
            print(f"エラー: {e}")
        
        print("-" * 50 + "\n")


if __name__ == "__main__":
    test_advanced_search()
    test_specific_search_types()
