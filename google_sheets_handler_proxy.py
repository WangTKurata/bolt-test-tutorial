import json
import os
import ssl

import certifi
import httplib2
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SSL証明書検証の問題を回避
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context


class GoogleSheetsHandlerProxy:
    def __init__(self, credentials_path, proxy_info=None):
        """
        Google Sheets APIを使用するためのハンドラーを初期化（プロキシ対応版）
        
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
        サービスアカウントを使用してGoogle Sheets APIに認証（プロキシ対応）
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
        スプレッドシートの全シートからデータを取得
        
        Args:
            spreadsheet_id (str): スプレッドシートのID
            
        Returns:
            list: 全シートのデータを含むリスト
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
                all_data.extend(values)
            
            return all_data
            
        except HttpError as e:
            print(f"データ取得エラー: {e}")
            return []
    
    def search_text_in_spreadsheet(self, spreadsheet_name, search_text):
        """
        指定されたスプレッドシート内でテキストを検索
        
        Args:
            spreadsheet_name (str): 検索対象のスプレッドシート名
            search_text (str): 検索するテキスト
            
        Returns:
            bool: テキストが見つかった場合True、見つからない場合False
        """
        try:
            # スプレッドシートを名前で検索
            spreadsheet_id = self.find_spreadsheet_by_name(spreadsheet_name)
            
            if not spreadsheet_id:
                print(f"スプレッドシート '{spreadsheet_name}' が見つかりません")
                return False
            
            # 全シートのデータを取得
            all_data = self.get_all_sheet_data(spreadsheet_id)
            
            # データ内でテキストを検索
            search_text_lower = search_text.lower()
            
            for row in all_data:
                for cell in row:
                    if cell and search_text_lower in str(cell).lower():
                        return True
            
            return False
            
        except Exception as e:
            print(f"検索エラー: {e}")
            return False


def search_in_target_spreadsheet_proxy(search_text, proxy_info=None):
    """
    指定されたスプレッドシートでテキストを検索する便利関数（プロキシ対応版）
    
    Args:
        search_text (str): 検索するテキスト
        proxy_info (dict): プロキシ情報 {'host': 'proxy.company.com', 'port': 8080}
        
    Returns:
        str: 検索結果メッセージ（「ありました」または「ありません」）
    """
    try:
        # 認証情報ファイルのパス
        credentials_path = ".vscode/boltslacktest-wang-40b68186e2db.json"
        
        # 検索対象のスプレッドシート名
        target_spreadsheet = "I want to use free software / フリーソフトを利用したい のコピー"
        
        # Google Sheetsハンドラーを初期化（プロキシ対応）
        sheets_handler = GoogleSheetsHandlerProxy(credentials_path, proxy_info)
        
        # テキストを検索
        found = sheets_handler.search_text_in_spreadsheet(target_spreadsheet, search_text)
        
        return "ありました" if found else "ありません"
        
    except Exception as e:
        print(f"検索処理エラー: {e}")
        return "検索中にエラーが発生しました"
