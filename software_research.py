import os

import openai

from google_sheets_handler_advanced import GoogleSheetsHandlerAdvanced


class SoftwareResearcher:
    def __init__(self, credentials_path, proxy_info=None):
        """
        ソフトウェア調査機能を初期化
        
        Args:
            credentials_path (str): Google Sheets認証情報のパス
            proxy_info (dict): プロキシ情報
        """
        self.credentials_path = credentials_path
        self.proxy_info = proxy_info
        self.sheets_handler = GoogleSheetsHandlerAdvanced(credentials_path, proxy_info)
        
        # OpenAI APIキーを設定
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY環境変数が設定されていません")
    
    def research_software(self, software_name):
        """
        ChatGPT APIを使用してソフトウェア情報を調査
        
        Args:
            software_name (str): 調査するソフトウェア名
            
        Returns:
            dict: 調査結果
        """
        try:
            prompt = f"""
以下のソフトウェアについて、セキュリティ観点から簡潔に調査してください：

ソフトウェア名: {software_name}

以下の項目について回答してください：
1. Category（カテゴリ）: どのような種類のソフトウェアか
2. Download page（ダウンロードページ）: 公式ダウンロードURL
3. Platform（プラットフォーム）: 対応OS（Windows, Mac, Linux等）
4. Remarks（備考）: セキュリティ上の注意点や特徴
5. Free version for commercial/corporate use（商用利用）: 企業での無料利用可否
6. Special remarks（特記事項）: その他重要な情報

各項目は簡潔に、1-2行程度で回答してください。
不明な場合は「不明」と記載してください。
"""

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはソフトウェアセキュリティの専門家です。企業環境でのソフトウェア利用について、セキュリティ観点から簡潔で正確な情報を提供してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            research_result = response.choices[0].message.content
            
            # 結果をパース
            parsed_result = self._parse_research_result(research_result)
            return parsed_result
            
        except Exception as e:
            print(f"ソフトウェア調査エラー: {e}")
            return {
                'category': '不明',
                'download_page': '不明',
                'platform': '不明',
                'remarks': '承認待ち',
                'free_commercial': '不明',
                'special_remarks': f'調査エラー: {str(e)}'
            }
    
    def _parse_research_result(self, research_text):
        """
        ChatGPTの調査結果をパースして構造化データに変換
        
        Args:
            research_text (str): ChatGPTからの応答テキスト
            
        Returns:
            dict: パースされた調査結果
        """
        result = {
            'category': '不明',
            'download_page': '不明',
            'platform': '不明',
            'remarks': '承認待ち',
            'free_commercial': '不明',
            'special_remarks': '不明'
        }
        
        lines = research_text.split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 各項目を識別
            if 'category' in line.lower() or 'カテゴリ' in line:
                current_field = 'category'
                # コロンの後の内容を取得
                if ':' in line:
                    result[current_field] = line.split(':', 1)[1].strip()
            elif 'download' in line.lower() or 'ダウンロード' in line:
                current_field = 'download_page'
                if ':' in line:
                    result[current_field] = line.split(':', 1)[1].strip()
            elif 'platform' in line.lower() or 'プラットフォーム' in line:
                current_field = 'platform'
                if ':' in line:
                    result[current_field] = line.split(':', 1)[1].strip()
            elif 'remarks' in line.lower() and 'special' not in line.lower() or '備考' in line:
                current_field = 'remarks'
                if ':' in line:
                    result[current_field] = line.split(':', 1)[1].strip()
            elif 'commercial' in line.lower() or '商用' in line:
                current_field = 'free_commercial'
                if ':' in line:
                    result[current_field] = line.split(':', 1)[1].strip()
            elif 'special' in line.lower() or '特記' in line:
                current_field = 'special_remarks'
                if ':' in line:
                    result[current_field] = line.split(':', 1)[1].strip()
            elif current_field and line and not any(keyword in line.lower() for keyword in ['category', 'download', 'platform', 'remarks', 'commercial', 'special']):
                # 継続行の場合
                if result[current_field] != '不明':
                    result[current_field] += ' ' + line
                else:
                    result[current_field] = line
        
        # 承認待ちをremarksに設定
        if result['remarks'] == '不明' or not result['remarks']:
            result['remarks'] = '承認待ち'
        else:
            result['remarks'] = '承認待ち - ' + result['remarks']
        
        return result
    
    def add_software_to_sheet(self, software_name, research_result):
        """
        調査結果をスプレッドシートに追加
        
        Args:
            software_name (str): ソフトウェア名
            research_result (dict): 調査結果
            
        Returns:
            bool: 追加成功の可否
        """
        try:
            # スプレッドシートを検索
            target_spreadsheet = "I want to use free software / フリーソフトを利用したい のコピー"
            spreadsheet_id = self.sheets_handler.find_spreadsheet_by_name(target_spreadsheet)
            
            if not spreadsheet_id:
                print(f"スプレッドシート '{target_spreadsheet}' が見つかりません")
                return False
            
            # 新しい行のデータを準備
            new_row = [
                software_name,  # Software Name
                research_result.get('category', '不明'),  # Category
                research_result.get('download_page', '不明'),  # Download page
                research_result.get('platform', '不明'),  # Platform
                research_result.get('remarks', '承認待ち'),  # Remarks
                '',  # application(Slack) - 空白
                research_result.get('free_commercial', '不明'),  # Free version for commercial/corporate use
                research_result.get('special_remarks', '不明')  # special remarks
            ]
            
            # スプレッドシートに行を追加
            # 注意: 実際の書き込みは読み取り専用権限では実行できないため、
            # ここでは追加予定の内容を返すのみとします
            return {
                'success': True,
                'data': new_row,
                'message': f"'{software_name}'の調査が完了しました。管理者による承認が必要です。"
            }
            
        except Exception as e:
            print(f"スプレッドシート追加エラー: {e}")
            return {
                'success': False,
                'data': None,
                'message': f"スプレッドシートへの追加中にエラーが発生しました: {str(e)}"
            }


def research_and_suggest_software(software_name, proxy_info=None):
    """
    ソフトウェアを調査して追加提案を行う便利関数
    
    Args:
        software_name (str): 調査するソフトウェア名
        proxy_info (dict): プロキシ情報
        
    Returns:
        dict: 調査結果と追加提案
    """
    try:
        # 認証情報ファイルのパス（環境変数から取得、デフォルトは汎用名）
        credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "google_service_account.json")
        researcher = SoftwareResearcher(credentials_path, proxy_info)
        
        # ソフトウェア調査
        research_result = researcher.research_software(software_name)
        
        # スプレッドシートへの追加提案
        add_result = researcher.add_software_to_sheet(software_name, research_result)
        
        return {
            'software_name': software_name,
            'research': research_result,
            'add_suggestion': add_result
        }
        
    except Exception as e:
        print(f"ソフトウェア調査・提案エラー: {e}")
        return {
            'software_name': software_name,
            'research': None,
            'add_suggestion': {
                'success': False,
                'message': f"調査中にエラーが発生しました: {str(e)}"
            }
        }
