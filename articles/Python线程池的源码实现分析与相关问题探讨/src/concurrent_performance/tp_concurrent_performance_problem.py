# Name: tp_concurrent_performance_problem
# Date: 2024-04-23
# Author: Ais
# Desc: 线程池并发性能的 “短板效应” 问题研究


import time
import json
import random
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed


class Task(object):
    """测试任务"""

    def __init__(self, tid, execute_time):
        # 任务id
        self.tid = tid
        # 模拟执行时间
        self.execute_time = execute_time

    def __repr__(self):
        return f'<Task({self.tid}) - execute_time({self.execute_time})>'

    def __call__(self):
        for i in range(self.execute_time):
            time.sleep(1)
            # print(f'[{current_thread().name}]({self.tid}): step({i})')


class TaskSource(object):
    """模拟的数据源"""

    def __init__(self, task_execute_time_rules):
        # 任务计数器
        self._task_counter = 0
        self._task_counter_lock = Lock()
        # 任务执行时间生成规则
        self._task_execute_time_rules = task_execute_time_rules

    def get(self, task_batch_size):
        """获取任务"""
        with self._task_counter_lock:
            tasks = []
            for i in range(task_batch_size):
                self._task_counter += 1
                tasks.append(Task(self._task_counter, self._task_execute_time_rules(self._task_counter)))
            return tasks
    
    def size(self):
        with self._task_counter_lock:
            return self._task_counter
    

class Dotter(Thread):
    """打点器"""

    def __init__(self, task_source, work_queue, dotting_interval=1, dotting_num=120):
        Thread.__init__(self)
        # 任务源
        self._task_source = task_source
        # 线程池工作队列
        self.work_queue = work_queue
        # 打点记录数据
        self._records = []
        self._step = 0
        # 打点间隔时间
        self._dotting_interval = dotting_interval
        # 打点次数
        self._dotting_num = dotting_num
        # 设置守护进程
        self.daemon = True

    def run(self):
        _task_size = self._task_source.size()
        for step in range(self._dotting_num):
            time.sleep(self._dotting_interval)
            task_size = self._task_source.size()
            record = {
                "step": step, 
                "task_size": task_size,
                "queue_size": self.work_queue.qsize(),
                "task_diff": task_size - _task_size
            }
            _task_size = task_size
            self._records.append(record)
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            print(f'[{self.__class__.__name__}][{t}]({record["step"]}): size({record["task_size"]}) - diff({record["task_diff"]}) - queue({record["queue_size"]})')
        with open('./concurrent_performance_records.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self._records, ensure_ascii=False))


if __name__ ==  "__main__":
    
    # 测试配置
    CONFIGS = {
        # 任务并发数
        "TP_MAX_WORKERS": 10,
        # 每次从任务源获取的任务数
        "TASK_BATCH_SIZE": 10,
        # 打点时间间隔
        "DOTTING_INTERVAL": 10,
        # 打点次数
        "DOTTING_NUM": 30,
        # 每批任务的超时时间
        # "TASK_TIMEOUT": 60 * 10,
        "TASK_TIMEOUT": 5,
        # 任务执行时间生成规则
        # "TASK_EXECUTE_TIME_RULES": lambda task_id: random.randint(3, 5),
        "TASK_EXECUTE_TIME_RULES": lambda task_id: random.randint(3, 5) if task_id % 20 else 10,
        "TASK_EXECUTE_TIME_RULES": lambda task_id: 5 if task_id % 10 else 10000,
    }

    task_source = TaskSource(CONFIGS["TASK_EXECUTE_TIME_RULES"])
    executor = ThreadPoolExecutor(max_workers=CONFIGS["TP_MAX_WORKERS"])
    
    Dotter(
        task_source = task_source,
        work_queue = executor._work_queue,
        dotting_interval = CONFIGS["DOTTING_INTERVAL"],
        dotting_num = CONFIGS["DOTTING_NUM"],
    ).start()

    while True:
        try:
            futures = [executor.submit(task) for task in task_source.get(task_batch_size=CONFIGS["TASK_BATCH_SIZE"])]
            results = [future.result() for future in as_completed(futures, timeout=CONFIGS["TASK_TIMEOUT"])]
        except: 
            pass
