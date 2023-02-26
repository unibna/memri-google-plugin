import pymemri
from pymemri.data.schema import *
from pymemri.pod.client import *

from loguru import logger

from google_service_plugin.data.schema import PluginRun,Account
from google_service_plugin.plugin import GoogleServicePlugin
from google_service_plugin.utils import setting, PluginService


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
    logger.debug("Create new pod client")
pod_client.add_to_schema(PluginRun, Account)

gg_svc_plugin = GoogleServicePlugin(
    client=pod_client,
)
gg_svc_plugin.install_plugin(
    name=setting.PLUGIN_NAME,
    containerImage=setting.PLUGIN_CONTAINER_NAME,
)
gg_svc_plugin.run_producer()
gg_svc_plugin.run_consumer()
