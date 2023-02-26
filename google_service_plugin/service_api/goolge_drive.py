from typing import (
    Optional,
    List,
    Dict,
    Any,
)

from google_service_plugin.service_api.google_service import GoogleService
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource
from google_service_plugin.utils import setting


class GoogleDriveService(GoogleService):

    def get_files(self) -> List[Dict[str, Any]]:
        folderId = self.service.files().list(
            # q="mimeType='image/jpeg'",
            # spaces='drive',
        ).execute()
        print(folderId)

        res = self.service.files().get(fileId='1aOw5LGok1uFZ7jAkJRvvYdFXzi6OWxzB').execute()
        print(res)

    def test(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        # Khởi tạo credentials
        creds = Credentials.from_authorized_user_info(
            info='/Users/duylannguyen/working/google_service_plugin/secrets/cloud_memri_service_account 02.00.24.json', 
            scopes=setting.GOOGLE_DRIVE_SCOPES,
        )
        # Khởi tạo credentials

        # Khởi tạo service
        service = build('drive', 'v3',credentials=creds)

        # Lấy danh sách tất cả các file
        files = []
        page_token = None
        while True:
            response = service.files().list(q="trashed=false",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                    'files(id, name, mimeType, modifiedTime)',
                                            pageToken=page_token).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        # In danh sách tên file
        for file in files:
            print(file.get('name'))
