# Name: test_work_thread_block
# Date: 2024-04-19
# Author: Ais
# Desc: 验证工作线程是否在队列为空时阻塞


import time
import threading
from concurrent.futures import ThreadPoolExecutor


def task():
    time.sleep(5)


executor = ThreadPoolExecutor(max_workers=3) 
[executor.submit(task) for i in range(3)]
# 由于无法监控线程的阻塞状态，因此手动绕过 self._work_queue.put(None) 逻辑观察线程池是否退出。
executor._shutdown = True

while True:
    print(f'[ThreadPoolExecutor]: threads({threading.active_count()}) shutdown({executor._shutdown})')
    time.sleep(1)


"""
# OUTPUT
[ThreadPoolExecutor]: threads(4) shutdown(True)
[ThreadPoolExecutor]: threads(4) shutdown(True)
[ThreadPoolExecutor]: threads(4) shutdown(True)
[ThreadPoolExecutor]: threads(4) shutdown(True)
[ThreadPoolExecutor]: threads(4) shutdown(True)
[ThreadPoolExecutor]: threads(4) shutdown(True)
"""