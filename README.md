# <center>自建免费IP代理池</center>
## 1.整体介绍
> 本项目总共包括8个模块，分别为：  
>   
  - `api.py`  
  - `db.py`  
  - `domain.py`  
  - `main.py`  
  - `run_spiders.py`
  - `setting.py`  
  - `spiders.py`  
  - `test.py`  
## 2.domain模块
> 1. 这个模块负责封装好爬取到的IP代理，也就是设计IP代理类，需要封装的属性包括IP地址，端口号，协议类型以及分数。  
2. 协议类型分为三种：0、1、2。
>> + 0代表IP支持http协议  
>> + 1代表IP支持https协议  
>> + 2代表http协议和https协议都支持  

> 3. 分数是用来评价爬取到的IP是否可用的。初始值为10，最大值为50。分数越高代表越可用。
## 3.db模块
> 这个模块负责设计存储IP代理的数据库操作接口，也就是IP池接口。包括的功能为：  
> 1. \_\_init\_\_:初始化数据库。数据库选择的是MongoDB数据库，个人感觉比较好用。初始化需要传入host和port，这些都在setting模块里设置好了。  
> 2.\_\_del\_\_:当删除MongoClient类时，关闭数据库。  
> 3.add:向数据库中添加一条IP代理。  
> 4.update：更新存储在数据库中的IP代理的信息。  
> 5.delete_one:从数据库中删除一条IP代理。  
> 6.remove:清空数据库。  
> 7.find_all：返回数据库中全部的IP代理，为了节省内存，使用生成器的形式。当然，返回的每一条IP代理都被封装为domain模块里的类的形式。  
> 8.find:传入protocol与count参数，protocol为字符串：'http','https'。count设置需要返回的 IP代理数量。根据这两个参数从数据库中返回满足条件的IP代理列表。特殊的是，返回的列表中的IP代理是根据IP的score分数排序从高到低返回的。  
> 9.random:随机返回一条满足protocol参数的IP代理。  
## 4.spiders模块
> 这个模块设计爬取从各个网站爬取免费IP代理的爬虫类。  
> **1.首先设计爬虫基类**：  
> BaseSpider：  
> 
> - \_\_init\_\_:有三个参数：urls, group_xpath, detail_xpath。urls传入待爬取页面的列表。group_xpath传入xpath路径的字符串，这个路径指向包含IP具体信息的上级HTML标签。detail_xpath则为group_xpath路径的后续路径，指明包含具体IP信息的标签。  
  - modification:通过xpath路径返回的为包含返回结果的列表，应该获取的是列表的索引为0的信息，而且还需要处理空列表的情况，为了避免重复劳动，所以放在这个函数中处理。  
  - get_page_from_url:指定requests需要的headers参数，返回要爬取页面的源代码。  
  - get_proxies:具体处理urls, group_xpath, detail_xpath参数,爬取IP代理。  

> **2.然后设计具体的爬虫类**：  
> 因为要爬取的网站不同，所以每个具体爬虫类除了要继承爬虫基类，还要为urls, group_xpath, detail_xpath参数赋予不同的值，甚至某些网站还存在反爬措施，所以还要根据情况修改get_page_from_url函数。
## 5.run_spiders模块
> 有了db模块与spiders模块，我们就可以设计运行爬虫类并将爬取到的IP代理存入数据库的模块了。  
> **RunSpider:**  
>  
>  - \_\_init\_\_:初始化MongoClient类以及协程池Pool类。
>  - get_spiders：在spiders模块中，我们设计了一些爬虫类，为了能在本模块中实例化它们，我们需要导入这些爬虫类，为此需要借助importlib库来导入它们。此函数返回爬虫类的实例的生成器。  
>  - execute_spider：有了爬虫类实例后，自然要执行它们，通过爬虫类的get_proxies()函数获得IP代理，并将IP代理添加进数据库中。  
>  - run：因为我们有多个爬虫实例，每个爬虫爬取不同的页面，有些页面可能有阻滞，这样程序就会一直等待某个页面，最好的做法就是通过协程，为每个爬虫分配协程，这样某个爬虫阻滞也不会影响其他爬虫爬取。这里使用gevent库来实现协程，要使用gevent库还需要在文件开头打个猴子补丁`from gevent import monkey`,`monkey.patch_all()`。  
>  - start：然后我们希望运行爬虫的程序每隔一定时间就再运行一次，所以我们写了一个类方法，通过schedule模块来实现程序的周期运行。
## 6.test模块  
> 这个模块负责检测已经存入数据库中的IP代理是否可用，然后更新其在数据库中的状态。  
> **ProxyTester：**  
> 
> - \_\_init\_\_:初始化MongoClient类、协程池Pool类、还有队列Queue类。
> - check_proxy：参数为proxy，也就是domain模块中类的实例。这个函数只需要判断从数据库中取出的IP代理是否可用，判断方法为通过requests库去获取响应，不成功则将proxy.protocol设置为-1，成功则根据情况将proxy.protocol设置为0、1、2。
> - run：从数据库中获取全部的IP代理，然后将每个IP代理添加入队列，使用队列是因为我们要用协程池去检测每个IP代理，为了避免重复处理，将IP代理加入队列中，每处理完一个pop一个，这样就可以避免重复。还有就是这里使用的协程只有10个，而IP代理的数量远远大于10个，所以就需要用到callback参数，不断回调async_callback函数，即一个协程处理完一个IP代理，继续处理下一个，直到队列为空。  
> - async_code：从队列中取出一个IP代理，使用check_proxy函数检测，然后根据proxy.protocol的值，决定如何修改proxy.score的值，并更新到数据库中。这里的打分规则是这样的，如果IP代理不可用，不是立即删除它，而是给它减一分，这样会有更多的容错率，而且因为初始值只有10分，不会让不可用IP代理难以删除。IP代理一旦可用，我们就将它的分数设置为最大值50分。  
> - async_callback：回调函数。因为callback只接受传入一个temp参数的函数，所以需要将`self.pool.apply_async(self.async_code, callback=self.async_callback)`封装入一个函数。  
> - start：同样，我们希望这个程序周期运行，此函数同run_spiders模块的start函数。  
## 7.api模块  
> 这个项目的目的是为了别的程序提供可用的IP代理的，所以我们需要设计一个接口，方便其他程序调用，从而获得可用的IP代理。而flask框架正好符合我们的需求。  
> **ProxyApi**： 
> 
> - \_\_init\_\_：初始化MongoClient类，以及Flask类。  
> - random：随机返回一个IP代理。这里使用了装饰器`@self.app.route("/random")`，这句话的作用是当在flask启动的地址后添加"/random"才会调用这个函数，这个函数还需要在url链接里加入protocol参数，指明想获取哪个协议类型的IP代理。  
> - get：返回指定协议类型和数量的IP代理字典。同样使用了装饰器。  
> - run：程序运行的函数。  
> - start：将运行函数封装入类方法。  