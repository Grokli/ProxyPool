from ProxyPool.setting import INITIAL_SCORE

class Proxy:
    def __init__(self, ip, port, protocol=-1, score=INITIAL_SCORE):
        self.ip = ip
        self.port = port
        self.protocol = protocol # 代理IP支持协议类型,http是0, https是1, https和http都支持是2
        self.score = score
