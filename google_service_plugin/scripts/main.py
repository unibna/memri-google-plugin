#!/usr/bin/python
import os
import sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_DIR.replace("/google_service_plugin/scripts", ""))

import pymemri
from pymemri.data.schema import *
from pymemri.pod.client import *

import getopt
from loguru import logger
from time import sleep
from requests.exceptions import ConnectionError

import helpers
from google_service_plugin.utils import *
from google_service_plugin.data.schema import *
from google_service_plugin.plugin import GoogleServicePlugin


def get_pod_client(host: str = 'http://localhost', port: str = '3030', version: str = 'v3',):
    DEFAULT_POD_ADDRESS = f"{host}:{port}"
    POD_VERSION = version

    attempt = 0
    while attempt < 3:
        try:
            pod_client = PodClient(
                database_key=setting.DATABASE_KEY,
                owner_key=setting.OWNER_KEY,
                create_account=False,
            )
            break
        except ConnectionError:
            logger.error(f"Attempt: {attempt + 1} failed.")
            sleep(5)
            attempt += 1
        except Exception as e:
            pod_client = PodClient(
                database_key=setting.DATABASE_KEY,
                owner_key=setting.OWNER_KEY,
            )
            logger.debug("[+] Create new pod client")
            break

    return pod_client


def main(argv):
    job = 'sync'
    service = 'google-photo'
    host = 'http://localhost'
    port = '3030'
    version = 'v3'

    try:
        opts, _ = getopt.getopt(argv,"hp:j:s:h:p",["service=","job=","host=","port=","version="])
    except getopt.GetoptError:
        print(helpers.DEFAULT)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(2)
            print(helpers.DEFAULT)
            sys.exit()
        elif opt in ("-j", "--job"):
            job = arg
        elif opt in ("-s", "--service"):
            service = arg
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-v", "--version"):
            version = arg

    if job == 'sync':
        # Init plugin
        pod_client = get_pod_client(host,port,version)
        plugin = GoogleServicePlugin(
            client=pod_client,
        )
        plugin.install_plugin(
            name=setting.PLUGIN_NAME,
            containerImage=setting.PLUGIN_CONTAINER_NAME,
        )
        plugin.run_producer(service=service)
        plugin.run_consumer()
    else:
        logger.error(f"The job: {job} is not supported.")


if __name__ == "__main__":
    main(sys.argv[1:])
