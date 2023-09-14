# Name: 
# Date: 2023-08-18
# Author: Ais
# Desc: None


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
    # "DUPEFILTER_CLASS": 'scrapy.dupefilters.RFPDupeFilter',
    # "JOBDIR": "./temp",
    "DUPEFILTER_CLASS": 'demo.dupefilters.LoaclPersistenceDupefilter',
    "DUPEFILTER_DIR": "./temp",
    # 采集范围
    "PAGES": (0, 10)
})

process = CrawlerProcess(settings)
[process.crawl(spider) for spider in process.spider_loader.list()]
process.start()