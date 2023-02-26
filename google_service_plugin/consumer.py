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

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from google_service_plugin.data.schema import QueueObject


def thread_safe(func):
    mutex = Lock()
    def wrapper(*args, **kwargs):
        with mutex:
            return func(*args, **kwargs)
    return wrapper


class PluginConsumer:

    def __init__(self, producer, maxsize: int = 10, **kwargs):
        
        self.max_retry = kwargs.get('max_retry', 5)
        self.wait_time = kwargs.get('wait_time', 1)
        self.delay_time = kwargs.get('delay_time', 0.25) # prevent full connection pool
        
        self.producer = producer

        self.maxsize = maxsize
        self.excutor = ThreadPoolExecutor(self.maxsize)
        self.futures = []

    @thread_safe
    def consume(self):
        while True:
            if not self.producer.queue.empty():
                obj = self.producer.queue.get()
                self.submit(obj)
                time.sleep(self.delay_time)
            else:
                logger.debug(f"Nothing in queue. Sleeping for {self.wait_time} seconds")
                time.sleep(self.wait_time)

    def submit(self, obj: QueueObject):
        self.futures.append(
            self.excutor.submit(obj.handler, obj.parameters)
        )

    def wait_futures(self):
        for job in self.futures:
            job.result()
