import requests
from lxml import etree
from ProxyPool.domain import Proxy
import time
import random


class BaseSpider:
    urls = []
    group_xpath = ''
    detail_xpath = {}

    def __init__(self, urls=[], group_xpath='', detail_xpath={}):
        if urls:
            self.urls = urls
        if group_xpath:
            self.group_xpath = group_xpath
        if detail_xpath:
            self.detail_xpath = detail_xpath

    def modification(self, data):
        return data[0].strip() if len(data) != 0 else ''

    def get_page_from_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        response = requests.get(url, headers=headers)
        return response.content


    def get_proxies(self):
        try:
            for url in self.urls:
                content = self.get_page_from_url(url)
                html = etree.HTML(content)
                trs = html.xpath(self.group_xpath)
                for tr in trs:
                    ip = self.modification(tr.xpath(self.detail_xpath['ip']))
                    port = self.modification(tr.xpath(self.detail_xpath['port']))
                    proxy = Proxy(ip, port)
                    yield proxy
        except Exception as e:
            print(e)


class XiciSpider(BaseSpider):
    urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 11)]
    group_xpath = '//*[@id="ip_list"]/tr[position()>1]'
    detail_xpath = {
        'ip':'./td[2]/text()',
        'port':'./td[3]/text()'
    }

class Ip3366Spider(BaseSpider):
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for j in range(1,8) for i in range(1, 3)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()'
    }

class IpKuaiSpider(BaseSpider):
    urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 6)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()'
    }

    def get_page_from_url(self, url):
        time.sleep(random.uniform(1, 3))
        return super().get_page_from_url(url)

class ProxylistplusSpider(BaseSpider):
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]
    group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'
    detail_xpath = {
        'ip':'./td[2]/text()',
        'port':'./td[3]/text()'
    }


class Ip66(BaseSpider):
    urls = ['http://www.66ip.cn/{}.html'.format(i) for i in range(1, 6)]
    group_xpath = '//*[@id="main"]/div/div[1]/table/tr[position()>1]'
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()'
    }

    def get_page_from_url(self, url):
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Cookie': '__jsluid_h=0350dbe37ef969d96fe54ed538cd2d32; __jsl_clearance=1564842300.279|0|cyjp5HtaUMWkOPWxzoHeY6HX4i4%3D; Hm_lvt_1761fabf3c988e7f04bec51acd4073f4=1564842304; Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4=1564844021'
        }
        response = requests.get(url, headers=headers)
        return response.content

if __name__ == '__main__':
    spider = XiciSpider()

    for proxy in spider.get_proxies():
        print(proxy)
