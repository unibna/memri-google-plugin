import os
import datetime
from typing import (
    Optional,
    Dict,
    List,
    Any,
)
from hashlib import sha256
from pydantic.dataclasses import dataclass


@dataclass
class PluginService:
    GOOGLE_PHOTO = 'google-photo'
    GOOGLE_DRIVE = 'google-drive'


class Settings:

    # Default directories
    ROOT_FOLDER = os.path.dirname(__file__)
    SECRETS_FOLDER = os.path.join(ROOT_FOLDER, 'secrets')
    SCRIPTS_FOLDER = os.path.join(ROOT_FOLDER, 'scripts')
    FILE_CACHE_FOLDER = os.path.join(ROOT_FOLDER, '__file_cache__')

    # Secret files
    GOOGLE_DRIVE_API_KEY = "AIzaSyCqRPXhFlXFOi8UDafadM5RgNByPdY0kyI"
    GOOGLE_PHOTO_CLIENT_ID_FILE = os.path.join(SECRETS_FOLDER, "google_photo_client_id.json")
    GOOGLE_PHOTO_TOKEN_FILE = os.path.join(SECRETS_FOLDER, "google_photo_token.pickle")
    GOOGLE_DRIVE_CLIENT_ID_FILE = os.path.join(SECRETS_FOLDER, "google_drive_client_id.json")
    GOOGLE_DRIVE_TOKEN_FILE = os.path.join(SECRETS_FOLDER, "google_drive_token.pickle")

    # PodClient Secrets
    DATABASE_KEY = f'googleServiceStorage'
    OWNER_KEY = f'googleServiceStorage'

    # Plugin Info
    PLUGIN_NAME = 'google_service_plugin'
    PLUGIN_CONTAINER_NAME = 'google_service_plugin'

    # Default scopes
    GOOGLE_PHOTO_SCOPES = [
        'https://www.googleapis.com/auth/photoslibrary.readonly',
    ]
    GOOGLE_DRIVE_SCOPES = [
        # 'https://www.googleapis.com/auth/drive',
        # '//www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]

    VIDEO_TYPES = ['video/mp4']
    IMGAE_TYPES = []
    THROTTLE = 1

    # Latest sync time
    GOOGLE_PHOTO_LATEST_SYNC_TIME = None
    GOOGLE_DRIVE_LATEST_SYNC_TIME = None


setting = Settings()


def datetime_to_dict(d: datetime.datetime):
    return {
        "day": d.day,
        "month": d.month,
        "year": d.year,
    }

def get_digest(blob: bytes):
    hasher = sha256()
    hasher.update(blob)
    return hasher.hexdigest()

def to_flat_dict(nested_dict: Dict[str, Any]) -> Dict[str, Any]:
    flat = {}
    for k, v in nested_dict.items():
        if isinstance(v, dict):
            flat[k] = to_flat_dict(v)
        else:
            flat[k] = v
    return flat
