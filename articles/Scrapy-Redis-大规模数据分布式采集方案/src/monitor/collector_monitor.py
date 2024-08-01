# Name: collector_monitor
# Date: 2024-07-26
# Author: Ais
# Desc: 监控采集进程的运行状态


import redis
import inspect


class CollectorMonitor(object):
    """采集器监控组件"""

    def __init__(self, service_name:str, spider_name:str, redis_params:dict, redis_keys:dict=None, metrics_prefix="collector"):
        # 测量值前缀
        self.metrics_prefix = metrics_prefix
        # 采集服务名
        self.service_name = service_name
        # 爬虫名
        self.spider_name = spider_name
        # 连接 redis 服务
        self.redis_connect = redis.Redis(**redis_params)
        
        redis_keys = redis_keys or {}
        # 任务队列
        self.task_queue = redis_keys["task_queue"]
        # 请求队列
        self.request_queue = redis_keys.get("request_queue", f'{self.spider_name}:requests')
        # 去重集
        self.dupefilter = redis_keys.get("dupefilter", f'{self.spider_name}:dupefilter')
        # 运行状态集
        self.stats = redis_keys.get("stats", f'{self.spider_name}:stats')

        # 计数方法映射
        self._count_size_method_map = {
            "list": self.redis_connect.llen,
            "set": self.redis_connect.scard,
            "zset": self.redis_connect.zcard,
        }
        # 计数方法缓存
        self._count_size_method_cache = {}

    def metrics(self) -> str:
        """测量"""
        _metrics = []
        for metric_method_name, metric_method in inspect.getmembers(self, inspect.ismethod):
            if not metric_method_name.startswith("metric_"):
                continue
            _metrics.append(metric_method())
        return "\n".join(_metrics)

    def _count_size(self, redis_key) -> int:
        """统计指定键的数据长度"""
        # 获取 redis 对应的计数方法
        if not self.redis_connect.exists(redis_key):
            return 0
        count_size_method = self._count_size_method_cache.setdefault(
            redis_key,
            self._count_size_method_map[self.redis_connect.type(redis_key).decode("utf-8")]         
        )
        return count_size_method(redis_key)
    
    def _metric(self, metric_name:str, metric_value=None, metric_type:str="", metric_desc="", metric_labels=None) -> str:
        """构建测量值"""
        metric_labels = {"service": self.service_name, "spider": self.spider_name, **(metric_labels or {})} 
        metric_labels = ", ".join([f'{k}="{v}"' for k, v in metric_labels.items()])
        metric = []
        metric_desc and metric.append(f'# HELP {metric_name} {metric_desc}')
        metric_type and metric.append(f'# TYPE {metric_name} {metric_type}')
        (metric_value is not None) and metric.append(f'{metric_name} {{{metric_labels}}} {metric_value}')
        return "\n".join(metric)

    def metric_task_queue(self) -> str:
        """测量任务队列指标"""
        return self._metric(
            metric_name = f'{self.metrics_prefix}_task_queue_size',
            metric_desc = "collector service redis task_queue size metric",
            metric_type = "gauge",
            metric_value = self._count_size(self.task_queue),
        )

    def metric_request_queue(self) -> str:
        """测量请求队列指标"""
        return self._metric(
            metric_name = f'{self.metrics_prefix}_request_queue_size',
            metric_desc = "collector service redis request_queue size metric",
            metric_type = "gauge",
            metric_value = self._count_size(self.request_queue),
        )

    def metric_dupefilter(self) -> str:
        """测量去重集指标"""
        return self._metric(
            metric_name = f'{self.metrics_prefix}_dupefilter_size',
            metric_desc = "collector service redis dupefilter set size metric",
            metric_type = "gauge",
            metric_value = self._count_size(self.dupefilter),
        )

    def metric_stats(self) -> str:
        """测量运行状态指标"""
        stats = {k.decode("utf-8"):v.decode("utf-8") for k, v in self.redis_connect.hgetall(self.stats).items()}
        metrics = [
            self._metric(
                metric_name = f'{self.metrics_prefix}_downloader_request_count',
                metric_desc = "collector service downloader processed request num",
                metric_type = "counter",
                metric_value = stats.get("downloader/request_count") or 0
            ),
            self._metric(
                metric_name = f'{self.metrics_prefix}_downloader_response_count',
                metric_desc = "collector service downloader processed response num",
                metric_type = "counter",
                metric_value = stats.get("downloader/response_count") or 0
            ),
            self._metric(
                metric_name = f'{self.metrics_prefix}_downloader_response_bytes',
                metric_desc = "collector service downloader processed response bytes",
                metric_type = "counter",
                metric_value = stats.get("downloader/response_bytes") or 0
            ),
            self._metric(
                metric_name = f'{self.metrics_prefix}_scraped_item_count',
                metric_desc = "collector service scraped item num",
                metric_type = "counter",
                metric_value = stats.get("item_scraped_count") or 0
            ),
        ]
        response_status_count = [self._metric(
            metric_name = f'{self.metrics_prefix}_downloader_response_status_count',
            metric_desc = "collector service downloader response_status(200, 404, ...) count",
            metric_type = "counter",
        )]
        for stats_name, stats_value in stats.items():
            if not stats_name.startswith("downloader/response_status_count/"):
                continue
            response_status_count.append(
                self._metric(
                    metric_name = f'{self.metrics_prefix}_downloader_response_status_count',
                    metric_labels = {"status_code": stats_name.split("/")[-1]},
                    metric_value = stats_value
                )
            )
        metrics.append("\n".join(response_status_count))
        return "\n".join(metrics)