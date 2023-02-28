import os
import sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_DIR.replace("/google_service_plugin/test", ""))

import json
import pymemri
from pymemri.data.schema import *
from pymemri.pod.client import *

from loguru import logger

from google_service_plugin.data.schema import *
from google_service_plugin.plugin import GoogleServicePlugin
from google_service_plugin.utils import setting, PluginService, to_flat_dict


DEFAULT_POD_ADDRESS = "http://localhost:3030"
POD_VERSION = "v3"


try:
    pod_client = PodClient(
        database_key=setting.DATABASE_KEY,
        owner_key=setting.OWNER_KEY,
        create_account=False,
    )
except:
    pod_client = PodClient(
        database_key=setting.DATABASE_KEY,
        owner_key=setting.OWNER_KEY,
    )
    logger.debug("[+] Create new pod client")

### Create test's data folder
DATA_FOLDER = os.path.join(BASE_DIR, 'data-test')
if not os.path.exists(DATA_FOLDER) or not os.path.isdir(DATA_FOLDER):
    os.mkdir(DATA_FOLDER)


def load_data_test(fp):
    with open(fp, 'r') as file:
        raw_data = file.read()
        raw_data = json.loads(raw_data)
        json_data = to_flat_dict(raw_data)
        return json_data


def test_init_image():
    fp = os.path.join(DATA_FOLDER, 'image_1.json')
    params = load_data_test(fp)
    params['mediaItemId'] = params['id'] 
    params.pop('id')
    params.pop('mediaMetadata')
    image_1 = Image(**params)
    pod_client.create(image_1)


def test_init_image_from_json():
    fp = os.path.join(DATA_FOLDER, 'image_2.json')
    json_data = load_data_test(fp)
    image_2 = Image.from_json(json_data)
    pod_client.create(image_2)


def test_init_video():
    fp = os.path.join(DATA_FOLDER, 'video_1.json')
    params = load_data_test(fp)
    params['mediaItemId'] = params['id'] 
    params.pop('id')
    params.pop('mediaMetadata')
    video_1 = Image(**params)
    pod_client.create(video_1)


def test_init_video_from_json():
    fp = os.path.join(DATA_FOLDER, 'video_2.json')
    json_data = load_data_test(fp)
    video_2 = Image.from_json(json_data)
    pod_client.create(video_2)
