from flask import Flask
from flask import request
from ProxyPool.db import MongoClient
import json


class ProxyApi:
    def __init__(self):
        self.app = Flask(__name__)
        self.collection = MongoClient()

        @self.app.route("/random")
        def random():
            protocol = request.args.get('protocol')
            proxy = self.collection.random(protocol)
            if protocol:
                return '{}://{}:{}'.format(protocol, proxy.ip, proxy.port)
            else:
                return '{}:{}'.format(proxy.ip, proxy.port)

        @self.app.route("/get")
        def get():
            protocol = request.args.get('protocol')
            count = request.args.get('count')
            if count is not None:
                count = int(count)
            else:
                count = 1
            proxies = self.collection.find(protocol, count)
            proxies = [i.__dict__ for i in proxies]
            return json.dumps(proxies)

    def run(self):
        self.app.run()

    @classmethod
    def start(cls):
        proxy_api = cls()
        proxy_api.run()


