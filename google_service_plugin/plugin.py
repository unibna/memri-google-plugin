import os
import time
from typing import (
    Optional,
    Dict,
    Any,
)
from loguru import logger

from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from google_service_plugin.service_api import GooglePhotoService, GoogleDriveService
from google_service_plugin.data import Image, Video, QueueObject
from google_service_plugin.plugin_flow import PluginFlow
from .producer import PluginProducer
from .consumer import PluginConsumer
from .utils import (
    setting, 
    get_digest, 
    to_flat_dict,
)


class GoogleServicePlugin(PluginFlow):

    def __init__(self, client, plugin_id=None, run_id=None, **kwargs):
        super().__init__(client=client, plugin_id=plugin_id, run_id=run_id)
        
        # Plugin configuration
        self.page_size = kwargs.get('page_size', 10)
        self.max_workers = kwargs.get('max_workers', 5)
        self.max_size = kwargs.get('max_size', self.page_size * 3)

        # Handler
        self.add_to_schema()
        self.google_photo_service = GooglePhotoService(
                service_name="photoslibrary",
                api_version="v1",
                scopes=setting.GOOGLE_PHOTO_SCOPES,
                credentials_fp=setting.GOOGLE_PHOTO_CLIENT_ID_FILE,
                token_fp=setting.GOOGLE_PHOTO_TOKEN_FILE,
            )
        self.google_drive_service = GoogleDriveService(
                service_name='drive',
                api_version='v3',
                scopes=setting.GOOGLE_DRIVE_SCOPES,
                credentials_fp=setting.GOOGLE_DRIVE_CLIENT_ID_FILE,
                token_fp=setting.GOOGLE_DRIVE_TOKEN_FILE,
                api_key=setting.GOOGLE_DRIVE_API_KEY,
            )
        
        self.threads = []
        self.producer = PluginProducer()
        self.consumer = PluginConsumer(producer=self.producer)
        self.delay_time = 0.2 # prevent full connection pool
        self.last_sync_time = self.google_photo_service.get_latest_time()

    def __del__(self):
        for thread in self.threads:
            thread.join()

    def run_producer(self):
        t = Thread(target=self.google_photos_producer)
        self.threads.append(t)
        t.start()

    def run_consumer(self):
        t = Thread(target=self.consumer.consume)
        self.threads.append(t)
        t.start()

    def google_photos_producer(self):
        while True:
            logger.debug("Starting sync from Google Photos.")
            next_page_token = ''
            is_running = True

            while is_running:
                # Sync data
                media_items, next_page_token = self.google_photo_service.list_lastest(
                                                        last_sync_time=self.last_sync_time,
                                                        page_size=self.page_size,
                                                        page_token=next_page_token,
                                                    )

                # Create tasks
                for media_item in media_items:
                    self.producer.put(QueueObject(
                        parameters=media_item,
                        handler=self.store_media_item
                    ))

                self.consumer.wait_futures()

                # Loop break condition
                if not next_page_token:
                    is_running = False
            logger.debug("Stop sync from Google Photos.")
            
            self.google_photo_service.save_time()
            time.sleep(self.delay_time)

    def store_media_item(self, media_item: Dict[str, Any]) -> bool:
        fp = self.google_photo_service.download_media_item(media_item)
        filename = media_item.get('filename', '')
        item_type = media_item.get('mimeType', '')
        json_data = to_flat_dict(media_item)

        # Store file
        try:
            with open(fp, 'rb') as file:
                blob = file.read()
                digest = get_digest(blob)
                json_data['sha256'] = digest
                is_uploaded = self.client.upload_file(blob)
                if not is_uploaded:
                    logger.error(f"[-] Failed to upload file into Pod. File name: {filename}")
                os.remove(fp)
        except Exception as e:
            logger.error(f"Failed to upload file. Error: {e}")
            return

        if item_type in setting.VIDEO_TYPES:
            item = Video.from_json(json_data)
        else:
            item = Image.from_json(json_data)
        is_stored = self.client.create(item)
        return is_stored

    def add_to_schema(self):
        self.client.add_to_schema(
            Video,
            Image,
        )
