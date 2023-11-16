# Name: 测试采集器
# Date: 2023-11-13
# Author: Ais
# Desc: None


import scrapy


class TestCollector(scrapy.Spider):

    name = "test"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.pn = kwargs.get("pn", 100)

    def start_requests(self):
        for i in range(self.pn):
            yield scrapy.Request(
                url = f'http://127.0.0.1:8000/collector/{self.__class__.__name__}/{i}',
                callback = self.parse,
                dont_filter = True,
            )

    def parse(self, response):
        data = {
            "url": response.url,
            **response.json(),
        }
        self.logger.info(data)
        yield data