# Name: LoaclPersistenceDupefilter
# Date: 2023-08-18
# Author: Ais
# Desc: 针对 *增量型* 采集任务设计的 *持久化* 请求去重器


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