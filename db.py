import pymongo
from ProxyPool.setting import MONGO_HOST, MONGO_PORT
from ProxyPool.domain import Proxy
import random


class MongoClient:
    def __init__(self, host=MONGO_HOST, port=MONGO_PORT):
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client.ProxyPool
        self.collection = self.db.proxies

    def __del__(self):
        self.client.close()

    def add(self, proxy):
        result = self.collection.find_one({'ip':proxy.ip})
        if result is None:
            self.collection.insert_one(proxy.__dict__)
            print('插入代理：{}'.format(proxy.__dict__))

    def update(self, proxy):
        self.collection.update_one({'ip':proxy.ip}, {'$set': proxy.__dict__})

    def delete_one(self, proxy):
        self.collection.delete_one({'ip': proxy.ip})
        print('删除代理ip：{}'.format(proxy.__dict__))

    def remove(self):
        self.collection.remove()
        print('数据库已清空')

    def find_all(self):
        proxies = self.collection.find()
        for proxy in proxies:
            proxy.pop('_id')
            yield Proxy(**proxy)

    def find(self, protocol=None, count=1):
        condition = {}
        if protocol is None:
            condition['protocol'] = 2
        elif protocol.lower() == 'http':
            condition['protocol'] = {'$in': [0, 2]}
        else:
            condition['protocol'] = {'$in': [1, 2]}
        results = self.collection.find(condition, limit=count).sort('score', pymongo.DESCENDING)
        proxies = []
        for i in results:
            i.pop('_id')
            proxy = Proxy(**i)
            proxies.append(proxy)
        return proxies

    def random(self, protocol=None):
        count = self.collection.find().count()
        proxies = self.find(protocol, count=int(count/2))
        return random.choice(proxies)




