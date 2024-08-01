# Name: scrapy-redis队列监视器
# Date: 2024-07-24
# Author: Ais
# Desc: None


import time
import json
import redis
import signal
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker


class ScrapyRedisMonitor(object):
    """scrapy_redis队列监视器"""

    def __init__(self, redis_params:dict, task_queue_key:str, request_queue_key:str):
        # 连接 redis 服务器
        self.redis_connect = redis.Redis(**redis_params)
        # 任务队列键名
        self.task_queue_key = task_queue_key
        # 请求队列键名
        self.request_queue_key = request_queue_key

    def monitor(self, monitor_interval:int=1, export_path:str="./scrapy-redis-monitor.json"):
        """监控数据指标"""
        stop = False
        monitor_points = []
        
        def _monitor_exit(sig, frame):
            nonlocal stop
            stop = True
        signal.signal(signal.SIGINT, _monitor_exit)
        
        step = 0
        while not stop:
            time.sleep(monitor_interval)
            step += 1
            monitor_point = {
                "step": step,
                "time": int(time.time()*1000),
                "task_queue": self.redis_connect.llen(self.task_queue_key),
                "request_queue": self.redis_connect.zcard(self.request_queue_key)
            }
            monitor_points.append(monitor_point) 
            print(f'[ScrapyRedisMonitor](monitor): {list(monitor_point.values())}')

        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(monitor_points, ensure_ascii=False))
        
    def draw(self, monitor_points_file:str="./scrapy-redis-monitor.json"):
        """绘制图像"""
        monitor_points = pd.read_json(monitor_points_file)
        print(monitor_points.head())

        ax = plt.axes()
        ax.set_title("scrapy-redis redis queue monitor", fontsize=20)

        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

        ax.set_ylabel("task_queue_num(int)", color="deepskyblue", fontsize=15)
        ax.set_ylim((0, monitor_points["task_queue"].max()))

        plt.plot(
            monitor_points["step"].to_numpy(),
            monitor_points["task_queue"].to_numpy(),
            label="task_queue",
            color="deepskyblue",
        )

        plt.plot(
            monitor_points["step"].to_numpy(),
            monitor_points["request_queue"].to_numpy(),
            label="request_queue",
            color="red",
        )

        plt.hlines(
            monitor_points["task_queue"].max(), 
            monitor_points["step"].min(), 
            monitor_points["step"].max(),
            linestyles="--", 
            colors="blue",
        )

        plt.legend(fontsize=15)

        plt.show()


        
if __name__ ==  "__main__":
    
    monitor = ScrapyRedisMonitor(
        redis_params = {
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "password": "",
        },
        task_queue_key = "BBSCollector.taskqueue",
        request_queue_key = "BBSCollector:requests"
    )

    # monitor.monitor()

    monitor.draw()