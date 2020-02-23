from multiprocessing import Process
from ProxyPool.run_spiders import RunSpider
from ProxyPool.test import ProxyTester
from ProxyPool.api import ProxyApi



def run():
    process_list = []
    process_list.append(Process(target=RunSpider.start))
    process_list.append(Process(target=ProxyTester.start))
    process_list.append(Process(target=ProxyApi.start))

    for process in process_list:
        process.daemon = True
        process.start()


    for process in process_list:
        process.join()


if __name__ == '__main__':
    run()