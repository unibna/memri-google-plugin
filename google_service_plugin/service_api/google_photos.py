from typing import (
    Optional,
    Tuple,
    List,
    Dict,
    Any,
)
import datetime

from google_service_plugin.service_api.google_service import GoogleService
from google_service_plugin.utils import datetime_to_dict


class GooglePhotoService(GoogleService):

    def list_all(
        self, 
        page_size: int = 10, page_token: str = ''
    ) -> Tuple[List[Dict[str, Any]], str]:
        res = self.service.mediaItems().list(
            pageSize=page_size,
            pageToken=page_token,
        ).execute()
        media_items = res.get('mediaItems', [])
        next_token = res.get('nextPageToken', '')
        return media_items, next_token
    
    def list_by_timerange(
        self, 
        start_date: datetime.datetime,
        end_date: datetime.datetime = datetime.datetime.now(),
        page_size: int = 10,
        page_token: str = ''
    ) -> Tuple[List[Dict[str, Any]], str]:
        res = self.service.mediaItems().search(body={
                "pageSize": page_size,
                "pageToken": page_token,
                "filters": {
                    "dateFilter": {
                        "ranges": [
                            {
                            "startDate": datetime_to_dict(start_date),
                            "endDate": datetime_to_dict(end_date),
                            }
                        ]
                    }
                }
            }).execute()
        media_items = res.get('mediaItems', [])
        next_token = res.get('nextPageToken', '')
        return media_items, next_token

    def list_lastest(
        self,
        last_sync_time: datetime.datetime = None,
        page_size: int = 10,
        page_token: str = ''
    ) -> Tuple[List[Dict[str, Any]]]:
        if not last_sync_time:
            return self.list_all(page_size, page_token)
        else:
            return self.list_by_timerange(
                start_date=last_sync_time,
                page_size=page_size,
                page_token=page_token,
            )