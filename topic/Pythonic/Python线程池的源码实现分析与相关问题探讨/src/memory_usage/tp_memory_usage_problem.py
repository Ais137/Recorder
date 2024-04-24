# Name: tp_memory_usage_problem
# Date: 2024-04-22
# Author: Ais
# Desc: 线程池内存占用问题


import os
import time
import json
import psutil
import random
from concurrent.futures import ThreadPoolExecutor


class Task(object):
    """测试任务"""

    def __init__(self, data_size, execute_time_range):
        # 任务数据
        self.data_info = "A" * data_size
        # 执行时间范围
        self.execute_time_range = execute_time_range

    def __call__(self):
        time.sleep(random.randint(*self.execute_time_range))


class Dotter(object):
    """打点器"""
    
    def __init__(self, tp):
        # 线程池对象
        self.tp = tp
        # 记录数据
        self.records = []
        # 步数
        self.step = 0
    
    def dotting(self):
        """打点"""
        record = {
            "step": self.step,
            "queue_size": self.tp._work_queue.qsize(),
            "memory_usage": psutil.Process(os.getpid()).memory_info().rss,
        }
        self.records.append(record)
        print(f'[{self.step}]: queue_size({record["queue_size"]}) -> memory_usage({record["memory_usage"]})')
        self.step += 1



if __name__ ==  "__main__":

    # 测试配置
    CONFIGS = {
        # 任务并发数
        "TP_MAX_WORKERS": 10,
        # 每批添加的任务数量
        "TASK_BATCH_SIZE": 10,
        # 任务数据大小
        "TASK_DATA_SIZE": 20 * 1024,
        # 任务执行时间范围
        "TASK_EXECUTE_TIME_RANGE": (1, 5),
        # 打点时间间隔
        "DOTTING_INTERVAL": 0.5,
        # 打点次数
        "DOTTING_NUM": 240,
    }

    executor = ThreadPoolExecutor(max_workers=CONFIGS["TP_MAX_WORKERS"])
    # 构建打点器
    dotter = Dotter(executor)

    dotter.dotting()
    for i in range(CONFIGS["DOTTING_NUM"]):
        time.sleep(CONFIGS["DOTTING_INTERVAL"]) 
        # 模拟生产者向工作队列添加任务  
        [
            executor.submit(Task(CONFIGS["TASK_DATA_SIZE"], CONFIGS["TASK_EXECUTE_TIME_RANGE"])) 
            for i in range(CONFIGS["TASK_BATCH_SIZE"])
        ]
        dotter.dotting()

    executor.shutdown(wait=False)

    with open('./memory_usage_records.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(dotter.records, ensure_ascii=False))

