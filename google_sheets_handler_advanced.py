import difflib
import json
import os
import ssl

import certifi
import httplib2
from fuzzywuzzy import fuzz, process
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SSL証明書検証の問題を回避
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context


class GoogleSheetsHandlerAdvanced:
    def __init__(self, credentials_path, proxy_info=None):
        """
        Google Sheets APIを使用するためのハンドラーを初期化（高度な検索機能付き）
        
        Args:
            credentials_path (str): サービスアカウントの認証情報JSONファイルのパス
            proxy_info (dict): プロキシ情報 {'host': 'proxy.company.com', 'port': 8080}
        """
        self.credentials_path = credentials_path
        self.proxy_info = proxy_info
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """
        サービスアカウントを使用してGoogle Sheets APIに認証
        """
        try:
            # サービスアカウントの認証情報を読み込み
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly',
                       'https://www.googleapis.com/auth/drive.readonly']
            )
            
            # プロキシ設定を含むHTTPクライアントを作成
            if self.proxy_info:
                proxy_info = httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_HTTP,
                    self.proxy_info['host'],
                    self.proxy_info['port']
                )
                http = httplib2.Http(
                    proxy_info=proxy_info,
                    disable_ssl_certificate_validation=True
                )
            else:
                # 環境変数からプロキシ設定を取得
                http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
                https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
                
                if http_proxy or https_proxy:
                    # プロキシURLをパース
                    proxy_url = https_proxy or http_proxy
                    if '://' in proxy_url:
                        proxy_url = proxy_url.split('://', 1)[1]
                    
                    if ':' in proxy_url:
                        proxy_host, proxy_port = proxy_url.split(':', 1)
                        proxy_port = int(proxy_port)
                    else:
                        proxy_host = proxy_url
                        proxy_port = 8080
                    
                    proxy_info = httplib2.ProxyInfo(
                        httplib2.socks.PROXY_TYPE_HTTP,
                        proxy_host,
                        proxy_port
                    )
                    http = httplib2.Http(
                        proxy_info=proxy_info,
                        disable_ssl_certificate_validation=True
                    )
                else:
                    http = httplib2.Http(disable_ssl_certificate_validation=True)
            
            # 認証されたHTTPクライアントを作成
            from google_auth_httplib2 import AuthorizedHttp
            authorized_http = AuthorizedHttp(credentials, http=http)
            
            # Google Sheets APIサービスを構築
            self.service = build('sheets', 'v4', http=authorized_http)
            
            # Google Drive APIサービスも構築（ファイル検索用）
            self.drive_service = build('drive', 'v3', http=authorized_http)
            
        except Exception as e:
            print(f"認証エラー: {e}")
            raise
    
    def find_spreadsheet_by_name(self, spreadsheet_name):
        """
        指定された名前のスプレッドシートをGoogle Driveから検索
        
        Args:
            spreadsheet_name (str): 検索するスプレッドシートの名前
            
        Returns:
            str: スプレッドシートのID（見つからない場合はNone）
        """
        try:
            # Google Driveでスプレッドシートを検索
            query = f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]['id']  # 最初に見つかったファイルのIDを返す
            else:
                return None
                
        except HttpError as e:
            print(f"スプレッドシート検索エラー: {e}")
            return None
    
    def get_all_sheet_data(self, spreadsheet_id):
        """
        スプレッドシートの全シートからデータを取得（4行目以降のみ）
        
        Args:
            spreadsheet_id (str): スプレッドシートのID
            
        Returns:
            list: 全シートのデータを含むリスト（4行目以降）
        """
        try:
            # スプレッドシートのメタデータを取得してシート名を取得
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            all_data = []
            
            for sheet in sheets:
                sheet_name = sheet['properties']['title']
                
                # 各シートのデータを取得
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=sheet_name
                ).execute()
                
                values = result.get('values', [])
                
                # 4行目以降のデータのみを追加（インデックス3以降）
                if len(values) > 3:
                    for i, row in enumerate(values[3:], start=4):  # 4行目から開始
                        # 行番号情報を保持するために、行データと実際の行番号をタプルで保存
                        all_data.append((row, i))
            
            return all_data
            
        except HttpError as e:
            print(f"データ取得エラー: {e}")
            return []
    
    def exact_search(self, all_data, search_text):
        """
        完全一致検索
        
        Args:
            all_data (list): 検索対象のデータ
            search_text (str): 検索するテキスト
            
        Returns:
            list: マッチした結果のリスト
        """
        matches = []
        search_text_lower = search_text.lower()
        
        for row_idx, row in enumerate(all_data):
            for col_idx, cell in enumerate(row):
                if cell and search_text_lower == str(cell).lower():
                    matches.append({
                        'type': '完全一致',
                        'text': str(cell),
                        'position': f'行{row_idx+1}, 列{col_idx+1}',
                        'score': 100
                    })
        
        return matches
    
    def partial_search(self, all_data, search_text):
        """
        部分一致検索（1列目のみ、4行目以降）
        
        Args:
            all_data (list): 検索対象のデータ（行データと行番号のタプルのリスト）
            search_text (str): 検索するテキスト
            
        Returns:
            list: マッチした結果のリスト
        """
        matches = []
        search_text_lower = search_text.lower()
        
        for row_data, actual_row_num in all_data:
            # 1列目のみを検索（インデックス0）
            if len(row_data) > 0:
                cell = row_data[0]
                if cell and search_text_lower in str(cell).lower():
                    matches.append({
                        'type': '部分一致',
                        'text': str(cell),
                        'position': f'行{actual_row_num}, 列1',
                        'score': 90
                    })
        
        return matches
    
    def fuzzy_search(self, all_data, search_text, threshold=70):
        """
        あいまい検索（類似度検索）
        
        Args:
            all_data (list): 検索対象のデータ
            search_text (str): 検索するテキスト
            threshold (int): 類似度の閾値（0-100）
            
        Returns:
            list: マッチした結果のリスト
        """
        matches = []
        all_texts = []
        text_positions = {}
        
        # 全てのテキストを収集
        for row_idx, row in enumerate(all_data):
            for col_idx, cell in enumerate(row):
                if cell:
                    cell_text = str(cell)
                    all_texts.append(cell_text)
                    text_positions[cell_text] = f'行{row_idx+1}, 列{col_idx+1}'
        
        # fuzzywuzzyを使用して類似度検索
        fuzzy_matches = process.extract(search_text, all_texts, limit=10)
        
        for match_text, score in fuzzy_matches:
            if score >= threshold:
                matches.append({
                    'type': 'あいまい一致',
                    'text': match_text,
                    'position': text_positions[match_text],
                    'score': score
                })
        
        return matches
    
    def advanced_search_in_spreadsheet(self, spreadsheet_name, search_text, search_types=['exact', 'partial', 'fuzzy']):
        """
        指定されたスプレッドシート内で高度な検索を実行
        
        Args:
            spreadsheet_name (str): 検索対象のスプレッドシート名
            search_text (str): 検索するテキスト
            search_types (list): 検索タイプのリスト ['exact', 'partial', 'fuzzy']
            
        Returns:
            dict: 検索結果の詳細情報
        """
        try:
            # スプレッドシートを名前で検索
            spreadsheet_id = self.find_spreadsheet_by_name(spreadsheet_name)
            
            if not spreadsheet_id:
                return {
                    'found': False,
                    'message': f"スプレッドシート '{spreadsheet_name}' が見つかりません",
                    'matches': []
                }
            
            # 全シートのデータを取得
            all_data = self.get_all_sheet_data(spreadsheet_id)
            
            all_matches = []
            
            # 各検索タイプを実行
            if 'exact' in search_types:
                exact_matches = self.exact_search(all_data, search_text)
                all_matches.extend(exact_matches)
            
            if 'partial' in search_types:
                partial_matches = self.partial_search(all_data, search_text)
                all_matches.extend(partial_matches)
            
            if 'fuzzy' in search_types:
                fuzzy_matches = self.fuzzy_search(all_data, search_text)
                all_matches.extend(fuzzy_matches)
            
            # 重複を除去し、スコア順にソート
            unique_matches = {}
            for match in all_matches:
                key = f"{match['text']}_{match['position']}"
                if key not in unique_matches or unique_matches[key]['score'] < match['score']:
                    unique_matches[key] = match
            
            sorted_matches = sorted(unique_matches.values(), key=lambda x: x['score'], reverse=True)
            
            return {
                'found': len(sorted_matches) > 0,
                'message': f"'{search_text}'の検索結果: {len(sorted_matches)}件見つかりました" if sorted_matches else f"'{search_text}'は見つかりませんでした",
                'matches': sorted_matches[:10]  # 上位10件まで
            }
            
        except Exception as e:
            print(f"検索エラー: {e}")
            return {
                'found': False,
                'message': "検索中にエラーが発生しました",
                'matches': []
            }


def advanced_search_in_target_spreadsheet(search_text, search_types=['exact', 'partial', 'fuzzy'], proxy_info=None):
    """
    指定されたスプレッドシートで高度な検索を実行する便利関数
    
    Args:
        search_text (str): 検索するテキスト
        search_types (list): 検索タイプのリスト ['exact', 'partial', 'fuzzy']
        proxy_info (dict): プロキシ情報 {'host': 'proxy.company.com', 'port': 8080}
        
    Returns:
        dict: 検索結果の詳細情報
    """
    try:
        # 認証情報ファイルのパス（環境変数から取得、デフォルトは汎用名）
        credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "google_service_account.json")
        
        # 検索対象のスプレッドシート名
        target_spreadsheet = "I want to use free software / フリーソフトを利用したい のコピー"
        
        # Google Sheetsハンドラーを初期化（高度な検索機能付き）
        sheets_handler = GoogleSheetsHandlerAdvanced(credentials_path, proxy_info)
        
        # 高度な検索を実行
        result = sheets_handler.advanced_search_in_spreadsheet(target_spreadsheet, search_text, search_types)
        
        return result
        
    except Exception as e:
        print(f"検索処理エラー: {e}")
        return {
            'found': False,
            'message': "検索中にエラーが発生しました",
            'matches': []
        }
