import os
import sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_DIR.replace("/google_service_plugin/test", ""))

import datetime
from dateutil.relativedelta import relativedelta
from google_service_plugin.utils import setting
from google_service_plugin.service_api.google_photos import GooglePhotoService
from google_service_plugin.service_api.goolge_drive import GoogleDriveService


def get_media_items_test():
    photoSvc = GooglePhotoService(
            service_name="photoslibrary",
            api_version="v1",
            scopes=setting.GOOGLE_PHOTO_SCOPES,
            credentials_fp=setting.GOOGLE_PHOTO_CLIENT_ID_FILE,
            token_fp=setting.GOOGLE_PHOTO_TOKEN_FILE,
        )
    photoSvc.list()

    start_date = datetime.datetime.now() - relativedelta(years=10)
    end_date = datetime.datetime.now()
    photoSvc.search_by_timerange(
        start_date=start_date,
        end_date=end_date,
    )

get_media_items_test()


# def get_files_test():
#     driveSvc = GoogleDriveService(kwargs={
#         "service_name": "drive",
#         "api_version": "v3",
#         "scopes": setting.GOOGLE_DRIVE_SCOPES,
#         "credentials_fp": setting.GOOGLE_DRIVE_CLIENT_ID_FILE,
#         "token_fp": setting.GOOGLE_DRIVE_TOKEN_FILE,
#     })
#     driveSvc.get_files()
# get_files_test()
