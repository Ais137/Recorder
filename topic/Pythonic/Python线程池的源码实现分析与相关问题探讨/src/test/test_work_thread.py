# Name: test_work_thread_create
# Date: 2024-04-19
# Author: Ais
# Desc: 测试工作线程的创建


import time
import threading
from itertools import count
from concurrent.futures import ThreadPoolExecutor, as_completed


def task():
    """测试的任务函数"""
    time.sleep(5)

def dotter():
    """打点器"""
    step = count().__next__
    def dotting(event:str):
        print(f'[step]({step()}): workThreads({threading.active_count()-1}) -> {event}')
    return dotting


if __name__ ==  "__main__":
    
    dotting = dotter()

    dotting("test start")
    executor = ThreadPoolExecutor(max_workers=3)  
    dotting("ThreadPoolExecutor created")
    futures = []
    for i in range(5):
        futures.append(executor.submit(task))
        dotting(f"submit task({i+1})")
    results = [future.result() for future in as_completed(futures)]
    time.sleep(1)
    dotting("tasks completed")
    executor.shutdown()
    time.sleep(1)
    dotting("ThreadPoolExecutor shutdown")
    time.sleep(1)
    dotting("test end")


    """
    # OUTPUT
    [step](0): workThreads(0) -> test start
    [step](1): workThreads(0) -> ThreadPoolExecutor created
    [step](2): workThreads(1) -> submit task(1)
    [step](3): workThreads(2) -> submit task(2)
    [step](4): workThreads(3) -> submit task(3)
    [step](5): workThreads(3) -> submit task(4)
    [step](6): workThreads(3) -> submit task(5)
    [step](7): workThreads(3) -> tasks completed
    [step](8): workThreads(0) -> ThreadPoolExecutor shutdown
    [step](9): workThreads(0) -> test end
    """