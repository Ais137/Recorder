# Name: test_as_completed_timeout
# Date: 2024-04-24
# Author: Ais
# Desc: 测试 as_completed 的 timeout 参数是否会导致任务主动取消


import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


def task(tid, run_time):
    for i in range(run_time):
        time.sleep(1)
        print(f'[{threading.current_thread().name}]({tid}): step({i})')


executor = ThreadPoolExecutor(max_workers=3)
futures = [executor.submit(task, i, i*5) for i in range(1, 4)]
try:
    results = [future.result() for future in as_completed(futures, timeout=5)]
except: 
    print("as_completed timeout")
print("as_completed completed")


"""
[ThreadPoolExecutor-0_0](1): step(0)
[ThreadPoolExecutor-0_1](2): step(0)
[ThreadPoolExecutor-0_2](3): step(0)
[ThreadPoolExecutor-0_2](3): step(1)
[ThreadPoolExecutor-0_1](2): step(1)
[ThreadPoolExecutor-0_0](1): step(1)
[ThreadPoolExecutor-0_0](1): step(2)
[ThreadPoolExecutor-0_1](2): step(2)
[ThreadPoolExecutor-0_2](3): step(2)
[ThreadPoolExecutor-0_0](1): step(3)
[ThreadPoolExecutor-0_2](3): step(3)
[ThreadPoolExecutor-0_1](2): step(3)
as_completed timeout
as_completed completed
[ThreadPoolExecutor-0_1](2): step(4)
[ThreadPoolExecutor-0_2](3): step(4)
[ThreadPoolExecutor-0_0](1): step(4)
[ThreadPoolExecutor-0_1](2): step(5)
[ThreadPoolExecutor-0_2](3): step(5)
[ThreadPoolExecutor-0_2](3): step(6)
[ThreadPoolExecutor-0_1](2): step(6)
[ThreadPoolExecutor-0_1](2): step(7)
[ThreadPoolExecutor-0_2](3): step(7)
[ThreadPoolExecutor-0_2](3): step(8)
[ThreadPoolExecutor-0_1](2): step(8)
[ThreadPoolExecutor-0_2](3): step(9)
[ThreadPoolExecutor-0_1](2): step(9)
[ThreadPoolExecutor-0_2](3): step(10)
[ThreadPoolExecutor-0_2](3): step(11)
[ThreadPoolExecutor-0_2](3): step(12)
[ThreadPoolExecutor-0_2](3): step(13)
[ThreadPoolExecutor-0_2](3): step(14)
"""