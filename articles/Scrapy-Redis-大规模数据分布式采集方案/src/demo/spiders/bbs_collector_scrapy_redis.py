# Name: 论坛数据采集器(scrapy-redis架构)
# Date: 2024-07-17
# Author: Ais
# Desc: None


import json
import scrapy
from scrapy_redis.spiders import RedisSpider

from .bbs_collector_base import BBSCollectorBase


class BBSCollector(RedisSpider, BBSCollectorBase):

    name = "BBSCollector-scrapy-redis"
    # 监听的redis任务队列键名
    redis_key = "BBSCollector.taskqueue"
    # 每次获取的任务数量
    redis_batch_size = 10
    # redis_batch_size = 2

    custom_settings = {
        # redis连接参数
        "REDIS_PARAMS": {
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "password": "",
        },
        # 调度器类
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        # 持久化开关
        "SCHEDULER_PERSIST": True,
        # 调度器队列类
        "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.PriorityQueue",
        # 去重器类
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        # 状态统计类
        "STATS_CLASS": "scrapy_redis.stats.RedisStatsCollector",
        # 请求并发数
        "CONCURRENT_REQUESTS": 16,
        # 最大空闲时间
        # "MAX_IDLE_TIME_BEFORE_CLOSE": 10,
    }

    def make_request_from_data(self, data):
        task = json.loads(data)
        yield scrapy.Request(
            url = f'http://BBS/list/{task["forum_id"]}/{1}',
            meta = {
                "forum_id": task["forum_id"],
                "page": 1,
                "max_page": 3,
            },
            callback = self.collect_post_meta,
            errback = self.collect_error,
            dont_filter = True,
        )
