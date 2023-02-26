import os
import time
import pickle
import requests
from typing import (
    Optional,
    List,
    Dict,
    Any,
)
from loguru import logger

from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from google_service_plugin.data.schema import QueueObject


def thread_safe(func):
    mutex = Lock()
    def wrapper(*args, **kwargs):
        with mutex:
            return func(*args, **kwargs)
    return wrapper


class PluginProducer:

    def __init__(self, maxsize: int = 10, **kwargs):
        
        self.max_retry = kwargs.get('max_retry', 5)
        self.wait_time = kwargs.get('wait_time', 1)

        self.maxsize = maxsize
        self.queue = Queue(self.maxsize)

    @thread_safe
    def put(self, data) -> bool:
        attempt = 0

        while attempt < self.max_retry:
            if not self.queue.full():
                self.queue.put(data)
                return True
            else:
                time.sleep(self.wait_time)
            attempt += 1

        logger.error(f"[x] Max Attempt. Failed to put new data")
        return False

