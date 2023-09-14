# Name: test_spiders
# Date: 2023-08-18
# Author: Ais
# Desc: None


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
        dict(
            name = spider_name,
            # custom_settings = {
            #     # 持久化缓存目录
            #     "JOBDIR": f"./temp/{spider_name}/"
            # }
        )
    )

