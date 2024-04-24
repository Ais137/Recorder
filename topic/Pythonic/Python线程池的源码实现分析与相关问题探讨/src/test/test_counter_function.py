# Name: test_counter_function
# Date: 2024-04-19
# Author: Ais
# Desc: 测试 ThreadPoolExecutor._counter 属性的作用


import time
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor


def task():
    time.sleep(3)
    print(f'[WorkThread]({current_thread().name})')


with ThreadPoolExecutor() as executor:
    [executor.submit(task) for i in range(3)]

with ThreadPoolExecutor() as executor:
    [executor.submit(task) for i in range(3)]


"""
# OUTPUT
[WorkThread](ThreadPoolExecutor-0_0)
[WorkThread](ThreadPoolExecutor-0_1)
[WorkThread](ThreadPoolExecutor-0_2)
[WorkThread](ThreadPoolExecutor-1_1)
[WorkThread](ThreadPoolExecutor-1_2)
[WorkThread](ThreadPoolExecutor-1_0)
"""
    