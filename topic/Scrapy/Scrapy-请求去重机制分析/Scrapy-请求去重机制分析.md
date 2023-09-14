## Scrapy-请求去重机制分析

-------------------------------------------------------
## 1. 概述
本文主要介绍数据采集中 *Scrapy* 框架下的去重机制分析和默认去重器的持久化机制，与其在特定应用场景下的问题。

### Index
- [Scrapy-请求去重机制分析](#scrapy-请求去重机制分析)
- [1. 概述](#1-概述)
  - [Index](#index)
  - [Meta](#meta)
- [1. 问题场景](#1-问题场景)
- [2. 问题分析](#2-问题分析)
  - [2.1. Scrapy框架请求去重机制分析](#21-scrapy框架请求去重机制分析)
  - [2.2. 默认去重器 *RFPDupeFilter* 的持久化机制分析](#22-默认去重器-rfpdupefilter-的持久化机制分析)
  - [2.3. *CrawlerProcess* 启用 *RFPDupeFilter* 持久化机制导致的异常原因分析](#23-crawlerprocess-启用-rfpdupefilter-持久化机制导致的异常原因分析)
- [3. 解决方案](#3-解决方案)
- [4. 扩展](#4-扩展)
  - [4.1. 分布式集群模式下的去重机制](#41-分布式集群模式下的去重机制)
  - [4.2. 大规模数据场景的去重器设计(布隆过滤器)](#42-大规模数据场景的去重器设计布隆过滤器)
  - [4.3. 一种基于时间失效的去重机制设计](#43-一种基于时间失效的去重机制设计)

### Meta
```json
{
    "node": "C87A47CE-6FF1-9E0A-A924-6A8E43441B8F",
    "name": "Scrapy-请求去重机制分析",
    "author": "Ais",
    "date": "2023-08-21",
    "tag": ["数据采集", "scrapy", "去重", "dupefilter", "源码分析"]
}
```

-------------------------------------------------------
## 1. 问题场景
**请求去重机制** 是数据采集框架中的一个重要特性，通过对重复请求进行过滤，从而减少无效的IO资源消耗。

对于 *增量型* 数据采集项目，通常是通过监控某个入口页(列表页)，进行持续的采集，并通过去重(过滤)机制来识别增量数据进行后续处理。在使用 scrapy 框架构建项目时，对于某些采集场景，其原生的去重机制可能不太适用，因此需要对其进行自定义来满足业务需求。

比如在采用 *CrawlerProcess* 运行多个爬虫时，默认的 *RFPDupeFilter* 去重器在启用持久化时，会因为文件冲突导致无法正常运行。

-------------------------------------------------------
## 2. 问题分析

### 2.1. Scrapy框架请求去重机制分析
在scrapy框架中，可以在构建 *请求对象(scrapy.Request)* 时，通过指定 *dont_filter* 参数来控制请求过滤功能。

```py
yield scrapy.Request(
    url = "https://www.test.com/page/1/data",
    callback = self.parse_data,
    dont_filter = True
)
```

*dont_filter* 参数默认为 **False**, 这意味着重复请求将被框架过滤。

该参数在 *scrapy* 中的具体处理逻辑位于 *scrapy.core.scheduler* 调度器模块中的 *Scheduler.enqueue_request* 方法中，其源码如下:
```py
def enqueue_request(self, request):
    if not request.dont_filter and self.df.request_seen(request):
        self.df.log(request, self.spider)
        return False
    dqok = self._dqpush(request)
    ...
```

从源码可以看到，请求去重条件由两个子条件构成:
1. not request.dont_filter
2. self.df.request_seen(request)

其中第一个条件是在构建 *scrapy.Request* 时设置的 *dont_filter* 参数。当该条件满足时判断第二个子条件。下面来分析第二个子条件的判断逻辑。

该条件调用了 *self.df* 的 *request_seen* 方法，通过源码分析可以发现，*self.df* 对象的实际构建逻辑位于 *Scheduler.from_crawler* 类方法中。
```py
@classmethod
def from_crawler(cls, crawler):
    settings = crawler.settings
    dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
    dupefilter = create_instance(dupefilter_cls, settings, crawler)
    ...
```
*self.df* 实际上是项目配置中 *DUPEFILTER_CLASS* 指定的去重器类的对象实例。

在未手动配置该参数时，其默认配置为 *DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'*

因此 *RFPDupeFilter* 去重器作为框架的默认去重器，源码位于 *scrapy.dupefilters* 模块中。其中核心的去重逻辑位于 *RFPDupeFilter.request_seen* 方法中:
```py
def request_seen(self, request):
    fp = self.request_fingerprint(request)
    if fp in self.fingerprints:
        return True
    self.fingerprints.add(fp)
    if self.file:
        self.file.write(fp + '\n')
```
去重器通过 *self.request_fingerprint(request)* 方法为每一个请求生成一个指纹，并判断是否在 *self.fingerprints* 已采集指纹集合中，来实现去重逻辑。

*request_fingerprint* 请求指纹的核心生成逻辑位于 *scrapy.utils.request.request_fingerprint* 函数中。

```py
def request_fingerprint(request, include_headers=None, keep_fragments=False):
    if include_headers:
        include_headers = tuple(to_bytes(h.lower()) for h in sorted(include_headers))
    cache = _fingerprint_cache.setdefault(request, {})
    cache_key = (include_headers, keep_fragments)
    if cache_key not in cache:
        fp = hashlib.sha1()
        fp.update(to_bytes(request.method))
        fp.update(to_bytes(canonicalize_url(request.url, keep_fragments=keep_fragments)))
        fp.update(request.body or b'')
        if include_headers:
            for hdr in include_headers:
                if hdr in request.headers:
                    fp.update(hdr)
                    for v in request.headers.getlist(hdr):
                        fp.update(v)
        cache[cache_key] = fp.hexdigest()
    return cache[cache_key]
```

到此为止，关于 scrapy 中的默认去重机制和流程已经明了。框架在启动时会加载一个默认的请求去重器 *RFPDupeFilter*, 去重器会为每个请求生成一个指纹，并判断是否在已采集的指纹集合中。核心去重判断逻辑在调度器的 *Scheduler.enqueue_request* 方法中被调用，通过结合 *scrapy.Request* 的 *dont_filter* 参数和请求去重器的判断结果来决定是否对请求进行过滤。


### 2.2. 默认去重器 *RFPDupeFilter* 的持久化机制分析
默认配置下，*RFPDupeFilter* 的去重机制不是持久化的，其只在爬虫运行期间生效，这是由于 *self.fingerprints* 集合对象是内存中的，当爬虫重启时该对象会重新构建。这意味着在面对增量型采集项目时，无法达到去重过滤功能。

但是可以通过配置 *JOBDIR* 参数来启用 *RFPDupeFilter* 的持久化机制。

```py
def __init__(self, path=None, debug=False):
    self.file = None
    self.fingerprints = set()
    self.logdupes = True
    self.debug = debug
    self.logger = logging.getLogger(__name__)
    if path:
        self.file = open(os.path.join(path, 'requests.seen'), 'a+')
        self.file.seek(0)
        self.fingerprints.update(x.rstrip() for x in self.file)
```
在 *RFPDupeFilter* 类的初始化过程中可以发现，当 *path* 参数不为空时，*self.file* 属性会填充一个文件对象，同时将指定路径中的数据加载到 *self.fingerprints* 集合中。

而当 *self.file* 不为空时，核心去重方法 *request_seen* 的行为逻辑将会改变:   
```py
def request_seen(self, request):
    ...
    self.fingerprints.add(fp)
    if self.file:
       self.file.write(fp + '\n')
```
请求指纹会被同步写入本地文件中，指纹数据位于 *JOBDIR* 路径下的 *requests.seen* 文件中。数据样例如下:
```
94656b0d1ed5f4adc103b68bf19c2f597b08b8e7
b8bffcde56a789a6e1672a03ed892ab5941b4966
98bb859215449dbbdf29946921746c030c48cbfd
5b93159006e5d8ef98cc1e5602d91302a4a1d213
fcb944f14d5eb6b97d54b139dc5ffa9634f50bf6
......
```
因此通过这种方式实现了 *RFPDupeFilter* 去重机制的持久化。


### 2.3. *CrawlerProcess* 启用 *RFPDupeFilter* 持久化机制导致的异常原因分析
*CrawlerProcess* 用于在同一个进程中运行多个 *spider*, 在这种场景下，如果启用了 *RFPDupeFilter* 持久化机制将导致 *spider* 运行异常。测试代码如下:

* 爬虫模块
```py
# demo.spiders
import scrapy


# 测试爬虫(基类)
class BaseTestSpider(scrapy.Spider):

    name = "BaseTestSpider"

    @classmethod
    def from_crawler(cls, crawler):
        spider = cls(crawler.settings.get("PAGES"))
        spider._set_crawler(crawler)
        return spider
    
    def __init__(self, pages=None):
        self.pages = pages or (10, )

    def start_requests(self):
        for i in range(*self.pages):
            yield scrapy.Request(
                url = f'http://127.0.0.1:8000/spider/{self.__class__.__name__}/page/{i}',
                callback = self.parse,
                dont_filter = False
            )

    def parse(self, response):
        self.logger.info(f'[{self.__class__.__name__}]: {response.url}')

# 动态生成爬虫类(模拟多个爬虫的场景)
for name in "ABC":
    spider_name = f'TestSpider{name}'
    globals()[spider_name] = type(
        spider_name,
        (BaseTestSpider, ),
        dict(name = spider_name)
    )
```

* 启动器
```py
# demo.launch
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


settings = get_project_settings()
settings.update({
    "SPIDER_MODULES": ['demo.spiders'],
    "NEWSPIDER_MODULE": 'demo.spiders',
    # 日志配置
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": '[%(asctime)s](%(levelname)s): %(message)s',
    # 去重器配置
    "DUPEFILTER_CLASS": 'scrapy.dupefilters.RFPDupeFilter',
    "JOBDIR": "./temp",
    # 采集范围
    "PAGES": (0, 10)
})

# 启动多个spider
process = CrawlerProcess(settings)
[process.crawl(spider) for spider in process.spider_loader.list()]
process.start()
```

* 测试服务器
```py
# demo.test_server.py
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"status": 0, "path": self.path}).encode("utf-8"))

server = ThreadingHTTPServer(('', 8000), HTTPRequestHandler)
server.serve_forever()
```

初次运行上述测试代码会产生以下异常: 
```py
Traceback (most recent call last):
  File ".\launch.py", line 27, in <module>
    process.start()
  File "D:\Anaconda\lib\site-packages\scrapy\crawler.py", line 327, in start
    reactor.run(installSignalHandlers=False)  # blocking call
  File "D:\Anaconda\lib\site-packages\twisted\internet\base.py", line 1283, in run
    self.mainLoop()
  File "D:\Anaconda\lib\site-packages\twisted\internet\base.py", line 1292, in mainLoop
    self.runUntilCurrent()
--- <exception caught here> ---
  File "D:\Anaconda\lib\site-packages\twisted\internet\base.py", line 913, in runUntilCurrent
    call.func(*call.args, **call.kw)
  File "D:\Anaconda\lib\site-packages\scrapy\utils\reactor.py", line 50, in __call__
    return self._func(*self._a, **self._kw)
  File "D:\Anaconda\lib\site-packages\scrapy\core\engine.py", line 124, in _next_request
    if not self._next_request_from_scheduler(spider):
  File "D:\Anaconda\lib\site-packages\scrapy\core\engine.py", line 153, in _next_request_from_scheduler
    request = slot.scheduler.next_request()
  File "D:\Anaconda\lib\site-packages\scrapy\core\scheduler.py", line 107, in next_request
    request = self._dqpop()
  File "D:\Anaconda\lib\site-packages\scrapy\core\scheduler.py", line 141, in _dqpop
    return self.dqs.pop()
  File "D:\Anaconda\lib\site-packages\scrapy\pqueues.py", line 97, in pop
    q.close()
  File "D:\Anaconda\lib\site-packages\queuelib\queue.py", line 175, in close
    os.remove(self.path)
builtins.PermissionError: [WinError 32] 另一个程序正在使用此文件，进程无法访问。: './temp\\requests.queue/0'
```

通过上述异常信息可以看出，是因为文件读写冲突导致的。
实际上在 *scrapy* 官方文档中就说明了 *持久化作业* 不能被不同的爬虫之间进行共享
> To enable persistence support you just need to define a job directory through the JOBDIR setting. This directory will be for storing all required data to keep the state of a single job (i.e. a spider run). It’s important to note that this directory must not be shared by different spiders, or even different jobs/runs of the same spider, as it’s meant to be used for storing the state of a single job.  
> 
> 要启用持久性支持，只需定义 作业目录 通过 JOBDIR 设置。此目录将用于存储所有必需的数据，以保持单个作业（即spider运行）的状态。需要注意的是，该目录不能由不同的spider共享，甚至不能由同一spider的不同作业/运行共享，因为它是用来存储 单一的 工作。

*持久化机制* 的一般应用通常是在执行耗时较长的采集任务中实现断点采集功能，对于 *增量型* 采集框架来说，每次任务执行的时间较短，因此不需要对请求队列或状态进行持久化，只是需要一个持久化的去重机制来实现增量数据的识别，但是由于 *RFPDupeFilter* 去重器的持久化功能依赖于 *JOBDIR* 参数，而该参数将启用整个框架的持久化机制，因此为了适应多爬虫的持久化去重场景，需要自定义一种去重机制。

-------------------------------------------------------
## 3. 解决方案

一个最直接的解决方法是为每个 *spider* 分配一个不同的 *JOBDIR* 参数 :
```py
class TestSpider(scrapy.Spider):

    name = "test_spider"

    # 自定义配置
    custom_settings = {
        # 持久化缓存目录
        "JOBDIR": "./temp/test_spider/"
    }
    ...
```
但是这种方法的缺陷在于，在项目的爬虫规模过大时，每个爬虫都需要单独设置参数，同时还是会启用整个持久化机制，而不是只针对去重器。

另一个方案是替换框架默认的请求去重器(*RFPDupeFilter*)，通过前述去重器机制的源码分析可以知道，scrapy框架在构建去重器实例的时候，会通过 *DUPEFILTER_CLASS* 参数加载对应的去重器类，因此可以通过设置该参数来加载自定义的去重器。

为此设计了一个针对 *多爬虫运行* 场景的 *增量型* 采集模式下具有 *持久化机制* 的请求去重器。

*LoaclPersistenceDupefilter* 去重器的设计如下:
```py
import os
import json
from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import request_fingerprint


# 本地持久化去重器
class LoaclPersistenceDupefilter(BaseDupeFilter):

    @classmethod
    def from_crawler(cls, crawler):
        # 构建去重器目录
        dupefilter_dir = crawler.settings.get('DUPEFILTER_DIR', default="./temp")
        not os.path.exists(dupefilter_dir) and os.makedirs(dupefilter_dir)
        # 构建去重缓存文件路径
        dupefilter_filepath = os.path.join(dupefilter_dir, f'dupefilter_{crawler.spider.name}.json')
        # 构建实例
        return cls(dupefilter_filepath)
    
    def __init__(self, filepath):
        # 去重缓存文件路径
        self.dupefilter_filepath = filepath      
        # 去重集合
        self.dupefilter_set = set()

    # 核心去重逻辑
    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        if fp in self.dupefilter_set:
            return True
        self.dupefilter_set.add(fp)

    # 计算请求指纹
    def request_fingerprint(self, request):
        return request_fingerprint(request)

    # 加载缓存文件
    def open(self):
        if not os.path.exists(self.dupefilter_filepath):
            return
        with open(self.dupefilter_filepath, "r", encoding="utf-8") as f:
            self.dupefilter_set = set(json.loads(f.read()))

    # 保存缓存文件
    def close(self, reason):
        with open(self.dupefilter_filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(list(self.dupefilter_set), ensure_ascii=False))
```

*LoaclPersistenceDupefilter* 的设计思路很朴素，核心逻辑是在 *from_crawler* 方法中构建实例时，为每个爬虫设置一个单独的去重缓存文件路径，同时在 *open* 和 *close* 方法中进行去重数据的加载和备份。通过避免去重缓存文件的共用，来解决 *RFPDupeFilter* 的问题，同时这样做的另一个好处在于，可以单独管理不同爬虫之间的缓存数据。

通过以下方法启用自定义的请求去重器 : 

```py
# settings.py 
DUPEFILTER_CLASS = "custom.dupefilters.LoaclPersistenceDupefilter"
DUPEFILTER_DIR = "./temp"
# spider.py or launch.py
custom_settings = {
    "DUPEFILTER_CLASS": "custom.dupefilters.LoaclPersistenceDupefilter",
    "DUPEFILTER_DIR": "./temp"
}
```
其中 *DUPEFILTER_DIR* 参数指定了去重器的缓存文件目录。


-------------------------------------------------------
## 4. 扩展
上述请求去重机制的讨论是基于最简单的数据采集场景，在面对其他复杂场景时，需要将不同的请求去重方案整合到采集框架中。以下是一些更为复杂的场景下的请求去重方案样例。

### 4.1. 分布式集群模式下的去重机制
*scrapy-redis* 是基于 *scrapy* 的增强组件，使原生 *scrapy* 框架具有了分布式采集的功能。该组件通过重写了 *RFPDupeFilter* 去重器，使其可以在分布式场景下工作。核心源码如下: 
```py
# scrapy_redis.dupefilters.RFPDupeFilter
def request_seen(self, request):
    fp = self.request_fingerprint(request)
    # This returns the number of values added, zero if already exists.
    added = self.server.sadd(self.key, fp)
    return added == 0
```
其中 *self.server* 是一个 *redis* 连接实例，不同的集群节点通过共享一个 *redis(set)* 数据结构来实现分布式场景下的请求去重功能。

### 4.2. 大规模数据场景的去重器设计(布隆过滤器)
传统的去重器内部通常采用 *哈希表(set)* 数据结构来存储已抓取的请求指纹。但是在面对大规模数据的去重场景时，*set* 结构消耗的存储空间过大。因此可以通过一种基于 *Bitmap* 构建的 *布隆过滤器* 来应对这种去重场景。相对于 *set* 结构，*布隆过滤器* 在存储空间上有巨大的优势。具体的原理和实现方式在网上有很多完善的资料，就不在此赘述了。

### 4.3. 一种基于时间失效的去重机制设计
针对 *增量型* 数据采集场景，可以通过分析其采集逻辑，设计一种 **基于时间失效的去重机制**。

对于传统的去重器，其存储空间占用通常是递增的，随着系统运行时间越长，存储空间消耗就越大。那么是否可以通过设计某种算法或机制，使去重器的存储空间消耗随系统运行的消耗是稳定的。

通过对 *增量型* 采集框架的去重场景分析可以发现，对于请求去重器中的一条URL指纹通常只在一段时间内“有效”，这是由于 *增量型* 采集通常是持续的监控一个列表页的首页数据，随着目标网站的更新，数据会产生 *滚动* 的效果，因此对于一条URL指纹，如果两次采集的时间间隔内，该指纹对应的URL被 *滚动* 到后续页面，则在去重机制里，这条URL指纹数据将不会再被使用，这就导致了无效的存储空间占用。

一个初步思路是对每个URL指纹记录一个失效时间，超过时间后移除缓存数据来减少存储空间开销，同时也不会影响到去重机制。

上述方法只是针对特殊应用场景的一个初步构想，完整方案和可行性验证demo后续会进行单独的讨论和研究。
