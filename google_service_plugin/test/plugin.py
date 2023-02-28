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


def test_full_flow():
    pod_client.add_to_schema(PluginRun, Account)

    # Init plugin
    gg_svc_plugin = GoogleServicePlugin(
        client=pod_client,
    )
    gg_svc_plugin.install_plugin(
        name=setting.PLUGIN_NAME,
        containerImage=setting.PLUGIN_CONTAINER_NAME,
    )

    # Download flow
    media_items, _ = gg_svc_plugin.google_photo_service.list_lastest()
    for media_item in media_items:
        gg_svc_plugin.store_media_item(media_item)
