# Name: 状态统计数据上传扩展组件
# Date: 2023-11-13
# Author: Ais
# Desc: None


import json
import redis
import logging
from scrapy import signals
from twisted.internet import task
from scrapy.utils.misc import load_object


logger = logging.getLogger(__name__)


class StatsUploader(object):
    """上传运行状态统计数据进行持久化和集中存储"""

    """
    UPLOAD_ON_CLOSE : 在采集结束后上传状态统计数据。
    UPLOAD_ON_IDLE  : 在空闲时上传状态统计数据。
    UPLOAD_INTERVAL : 定时上传状态统计数据。
    """
    UPLOAD_MODE = ["UPLOAD_ON_CLOSE", "UPLOAD_ON_IDLE", "UPLOAD_INTERVAL"]

    def __init__(self, stats, connector, upload_mode="UPLOAD_ON_CLOSE", upload_interval=60, gen_spider_id=None):
        # 状态统计数据
        self.stats = stats
        # 数据库连接器
        self.connector = connector
        # 上传模式(UPLOAD_ON_CLOSE, UPLOAD_ON_IDLE, UPLOAD_INTERVAL)
        self.upload_mode = upload_mode 
        # 上传间隔
        self.upload_interval = upload_interval
        # 定时上传任务
        self._upload_task = None
        # 生成spider_id
        self.gen_spider_id = gen_spider_id or (lambda spider: spider.name)
        # 空闲上传模式数据上传标记(限制在进入空闲状态时只上传一次数据)
        self._idle_mode_uploaded_flag = False

    @classmethod
    def from_crawler(cls, crawler):
        # 构建连接器对象
        connect_confs = crawler.settings.get("STATSUPLOADER_CONNECT_CONFS")
        if crawler.settings.get("STATSUPLOADER_CONNECTOR_CLASS"):
            connector_class = load_object(crawler.settings.get("STATSUPLOADER_CONNECTOR_CLASS"))
        else:
            connector_class = RedisConnector
        connector = connector_class(**connect_confs)
        # 构建状态上传器对象
        stats_uploader = cls(
            stats = crawler.stats,
            connector = connector,
            upload_mode = crawler.settings.get("STATSUPLOADER_UPLOAD_MODE") or "UPLOAD_ON_CLOSE",
            upload_interval = crawler.settings.get("STATSUPLOADER_UPLOAD_INTERVAL") or 60,
            gen_spider_id = crawler.settings.get("STATSUPLOADER_GEN_SPIDERID"),
        )
        # 注册事件
        if stats_uploader.upload_mode == "UPLOAD_ON_IDLE":
            crawler.signals.connect(stats_uploader.spider_idle, signal=signals.spider_idle)
            crawler.signals.connect(stats_uploader.request_scheduled, signal=signals.request_scheduled)
        crawler.signals.connect(stats_uploader.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(stats_uploader.spider_closed, signal=signals.spider_closed)
        return stats_uploader
    
    def get_stats(self):
        """获取状态统计数据"""
        stats = self.stats.get_stats().copy()
        for k, v in stats.items():
            if type(v).__name__ == "datetime":
                stats[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        return stats
    
    def upload_stats(self, spider):
        """上传状态统计数据"""
        spider_id = self.gen_spider_id(spider)
        try:
            self.connector.upload(spider_id, self.get_stats())
            logger.info(f'collector({spider_id}) upload state success')
        except:
            logger.error(f'collector({spider_id}) upload state failed')

    def spider_opened(self, spider):
        if self.upload_mode == "UPLOAD_INTERVAL":
            self.upload_task = task.LoopingCall(self.upload_stats, spider)
            self.upload_task.start(self.upload_interval)
        hasattr(self.connector, "connect") and self.connector.connect()

    def spider_closed(self, spider, reason):
        if self.upload_task and self.upload_task.running:
            self.upload_task.stop()
        self.upload_stats(spider)
        hasattr(self.connector, "close") and self.connector.close()

    def spider_idle(self, spider):
        if self._idle_mode_uploaded_flag is False:
            self.upload_stats(spider)
            self._idle_mode_uploaded_flag = True

    def request_scheduled(self, request, spider):
        self._idle_mode_uploaded_flag = False


class RedisConnector(object):
    """连接redis进行数据上传"""

    def __init__(self, key, **kwargs):
        # 存储键名
        self._key = key
        # 连接配置
        self._connect_confs = kwargs
        # 连接实例
        self._redis_connect = None

    def connect(self):
        """连接redis"""
        if self._redis_connect is None:
            self._redis_connect = redis.Redis(**self._connect_confs)

    def upload(self, spider_id:str, stats:dict):
        """上传状态数据
        
        Args:
            * spider_id: 爬虫id
            * stats: 状态统计数据
        """
        if self._redis_connect:
            self._redis_connect.hset(self._key, spider_id, json.dumps(stats))

    def close(self):
        """释放连接"""
        if self._redis_connect:
            self._redis_connect.close()
            self._redis_connect = None