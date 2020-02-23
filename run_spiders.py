from gevent import monkey
monkey.patch_all()

from ProxyPool.db import MongoClient
from gevent.pool import Pool
from ProxyPool.setting import PROXY_SPIDERS
import importlib
import time
import schedule


class RunSpider:

    def __init__(self):
        self.collection = MongoClient()
        self.pool = Pool()

    def get_spiders(self):
        for i in PROXY_SPIDERS:
            module_name, class_name = i.split('.')
            module = importlib.import_module(module_name)
            spider = getattr(module, class_name)
            yield spider()

    def run(self):
        spiders = self.get_spiders()
        for spider in spiders:
            self.pool.apply_async(self.execute_spider, args=(spider, ))
        self.pool.join()

    def execute_spider(self, spider):
        for proxy in spider.get_proxies():
            self.collection.add(proxy)

    @classmethod
    def start(cls):
        rs = cls()
        rs.run()
        schedule.every(1).hours.do(rs.run())
        while True:
            schedule.run_pending()
            time.sleep(1800)


if __name__ == '__main__':
    RunSpider.start()