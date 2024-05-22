import scrapy


class TestspiderSpider(scrapy.Spider):

    name = 'testspider'

    # 数据源信息
    source = {
        "name": "",
        "url": "https://https://www.test.com/"
    }

    # 自定义配置
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {

        },
        "ITEM_PIPELINES": {

        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url = "",
            callback = self.parse,
            dont_filter = True,
        )