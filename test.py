from gevent import monkey
monkey.patch_all()

from gevent.pool import Pool
from queue import Queue
from ProxyPool.db import MongoClient
import requests
from ProxyPool.setting import MAX_SCORE
import schedule
import time


class ProxyTester:
    def __init__(self):
        self.collection = MongoClient()
        self.queue = Queue()
        self.pool = Pool()

    def run(self):
        proxies = self.collection.find_all()
        for proxy in proxies:
            self.queue.put(proxy)
        for i in range(10):
            self.pool.apply_async(self.async_code, callback=self.async_callback)
        self.queue.join()

    def async_callback(self, temp):
        self.pool.apply_async(self.async_code, callback=self.async_callback)

    def async_code(self):
        proxy = self.queue.get()
        proxy = self.check_proxy(proxy)
        if proxy.protocol == -1:
            proxy.score -= 1
            if proxy.score == 0:
                self.collection.delete_one(proxy)
            else:
                self.collection.update(proxy)
        else:
            proxy.score = MAX_SCORE
            self.collection.update(proxy)
        self.queue.task_done()

    def check_proxy(self, proxy):
        proxies = {
            'http':'http://{}:{}'.format(proxy.ip, proxy.port),
            'https':'https://{}:{}'.format(proxy.ip, proxy.port)
        }
        http_url = 'http://httpbin.org/get'
        https_url = 'https://httpbin.org/get'
        try:
            http_response = requests.get(http_url, proxies=proxies)
            https_response = requests.get(https_url, proxies=proxies)
            if http_response.ok and https_response.ok:
                proxy.protocol = 2
            elif http_response.ok:
                proxy.protocol = 0
            elif https_response.ok:
                proxy.protocol = 1
        except Exception:
            proxy.protocol = -1
        return proxy

    @classmethod
    def start(cls):
        proxy_tester = cls()
        proxy_tester.run()
        schedule.every(3).minutes.do(proxy_tester.run)
        while True:
            schedule.run_pending()
            time.sleep(30)


