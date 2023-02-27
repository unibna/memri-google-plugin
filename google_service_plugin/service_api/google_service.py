import os
import pickle
import urllib
import shutil
import requests
from datetime import datetime
from loguru import logger
from typing import (
    Optional,
    List,
    Any,
    Dict,
)

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource

from google_service_plugin.utils import setting


class GoogleService:

    file_cache_folder: str = setting.FILE_CACHE_FOLDER
    request_session = requests.Session()

    def __init__(self, **kwargs):
        self.service_name = kwargs.get('service_name', '')
        self.api_version = kwargs.get('api_version', '')
        self.scopes = kwargs.get('scopes', '')
        self.credentials = kwargs.get('credentials', '')
        self.credentials_fp = kwargs.get('credentials_fp', '')
        self.token_fp = kwargs.get('token_fp', '')
        self.api_key = kwargs.get('api_key', '')
        
        self.service = None

        if not self.credentials:
            if self.token_fp:
                self.credentials = self.get_credentials(
                    credentials_fp=self.credentials_fp,
                    token_fp=self.token_fp,
                    scopes=self.scopes,
                )

        if self.api_key:
            self.service: Resource = self.get_service(
                service_name=self.service_name,
                version=self.api_version,
                api_key=self.api_key,
            )
        
        if self.credentials:
            self.service: Resource = self.get_service(
                service_name=self.service_name,
                version=self.api_version,
                credentials=self.credentials,
            )

    @classmethod
    def get_credentials(
        cls, 
        credentials_fp: str = '', token_fp: str = '',
        scopes: List[str] = [],
    ) -> Credentials:
        creds = None
        if os.path.exists(token_fp):
            with open(token_fp, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_fp, 
                    scopes=scopes,
                )
                creds = flow.run_local_server()
            with open(token_fp, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    @classmethod
    def get_service(
        cls,
        credentials: Credentials = None,
        api_key: str = '',
        static_discovery: bool = False,
        service_name: str = '',
        version: str = '',
    ) -> Optional[Resource]:
        if credentials:
            service = build(
                serviceName=service_name,
                version=version,
                credentials=credentials,
                static_discovery=static_discovery,
            )
            return service
        
        if api_key:
            service = build(
                serviceName=service_name,
                version=version,
                developerKey=api_key,
            )
            return service

    @classmethod
    def download_file(
        cls,
        url: str,
        file_name: str,
        chunk_size: int = 1024,
    ) -> Optional[str]:
        # logger.debug(f"[+] Downloading file: {file_name}")
        if not os.path.isdir(cls.file_cache_folder):
            os.mkdir(cls.file_cache_folder)
        
        try:
            full_fp = os.path.join(cls.file_cache_folder, file_name)
            response = cls.request_session.get(url, stream=True)
            with open(full_fp, 'wb') as f:
                for data in response.iter_content(chunk_size):
                    f.write(data)
            return full_fp
        except Exception as e:
            logger.error(f"Failed to download file - {file_name}. Error: {e}")
    
    @classmethod
    def download_media_item(cls, media_item: Dict[str, Any]):
        url = media_item.get('baseUrl', '')
        filename = media_item.get('filename', '')
        return cls.download_file(url, filename)
    
    @classmethod
    def clear_file_cache_folder(cls):
        if os.path.isdir(cls.file_cache_folder):
            files = os.listdir(cls.file_cache_folder)
            for file in files:
                os.remove(os.path.join(cls.file_cache_folder, file))
            logger.debug(f"Clear file cache folder. Total: {len(files)}")

    def save_time(self, lastest_time: datetime = None):
        fp = os.path.join(setting.SECRETS_FOLDER, f'save-time-{self.service_name}.txt')
        with open(fp, 'w') as file:
            try:
                data = lastest_time.strftime('%Y-%m-%d')
            except:
                data = datetime.now().strftime('%Y-%m-%d')
            file.write(data)
            logger.debug(f"Save latest time for service {self.service_name}. Time: {data}")

    def get_latest_time(self):
        try:    
            fp = os.path.join(setting.SECRETS_FOLDER, f'save-time-{self.service_name}.txt')
            with open(fp, 'r') as file:
                data = file.read()
                latest_time = datetime.strptime(data, '%Y-%m-%d')
        except:
            latest_time = None

        logger.debug(f"Get latest time for service {self.service_name}. Time: {latest_time}")
        return latest_time
