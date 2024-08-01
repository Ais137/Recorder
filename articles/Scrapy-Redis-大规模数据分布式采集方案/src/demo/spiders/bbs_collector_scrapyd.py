# Name: 论坛数据采集器(scrapyd分片任务架构)
# Date: 2024-07-16
# Author: Ais
# Desc: scrapyd分片任务架构


import scrapy
from .bbs_collector_base import BBSCollectorBase


class BBSCollector(scrapy.Spider, BBSCollectorBase):

    name = "BBSCollector-scrapyd"

    def __init__(self, task_part_id=None, *args, **kwargs):
        super(BBSCollector, self).__init__(*args, **kwargs)
        # 任务分片id
        self.task_part_id = task_part_id or 0

    def start_requests(self):
        # 通过任务分片id, 获取待采集目标论坛id列表
        yield scrapy.Request(
            url = f'http://127.0.0.1:8081/task/part/{self.task_part_id}',
            callback = self.build_request_from_forum_ids,
            errback = self.collect_error,
            dont_filter = True,
        )

    def build_request_from_forum_ids(self, response):
        """构建列表数据接口初始请求"""
        data = response.json()
        if data["state"]:
            target_forum_ids = data.get("tasks") or []
            self.logger.info(f'[{self.name}](build): start tasks({target_forum_ids})')
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
        else:
            self.logger.error(f'[{self.name}](build): get task_part({self.task_part_id}) failed')
