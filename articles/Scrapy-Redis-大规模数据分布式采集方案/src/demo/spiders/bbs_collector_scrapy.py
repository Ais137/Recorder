# Name: 论坛数据采集器(scrapy架构)
# Date: 2024-07-16
# Author: Ais
# Desc: None


import scrapy
from .bbs_collector_base import BBSCollectorBase


class BBSCollector(scrapy.Spider, BBSCollectorBase):

    name = "BBSCollector-scrapy"

    def start_requests(self):
        # 待采集目标论坛id列表
        target_forum_ids = ["00001", "00002", "00003", "00004", "00005"]
        # 构建列表数据接口初始请求
        for forum_id in target_forum_ids:
            yield scrapy.Request(
                url = f'http://BBS/list/{forum_id}/{1}',
                meta = {
                    "forum_id": forum_id,
                    "page": 1,
                    "max_page": 5,
                },
                callback = self.collect_post_meta,
                errback = self.collect_error,
                dont_filter = True,
            )
