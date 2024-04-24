# Name: test_gc_trigger_exit
# Date: 2024-04-19
# Author: Ais
# Desc: 线程池对象被垃圾回收触发工作线程的销毁机制


import time
import weakref
import threading
from itertools import count
from concurrent.futures import ThreadPoolExecutor


def task():
    """测试任务函数"""
    time.sleep(5)

executor_reference = None
def tarck_executor_reference():
    """追踪 executor 的引用"""
    step = count().__next__
    def tracker():
        global executor_reference
        print(f'[step]({step()}): workThreads({threading.active_count()-1}) --- ref({executor_reference})')
    return tracker
tracker = tarck_executor_reference()

def main():
    tracker()
    executor = ThreadPoolExecutor(max_workers=3) 
    global executor_reference
    def weakref_cb(_):
        print("executor is garbage collected")
    executor_reference = weakref.ref(executor, weakref_cb)
    tracker()
    [executor.submit(task) for i in range(10)]
    tracker()
main()

while True:
    time.sleep(1)
    tracker()
    if threading.active_count() == 1:
        break


"""
# OUTPUT
[step](0): workThreads(0) --- ref(None)
[step](1): workThreads(0) --- ref(<weakref at 0x000001EED4C2B220; to 'ThreadPoolExecutor' at 0x000001EED4B72070>)
[step](2): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; to 'ThreadPoolExecutor' at 0x000001EED4B72070>)
executor is garbage collected
[step](3): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](4): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](5): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](6): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](7): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](8): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](9): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](10): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](11): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](12): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](13): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](14): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](15): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](16): workThreads(3) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](17): workThreads(1) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](18): workThreads(1) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](19): workThreads(1) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](20): workThreads(1) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](21): workThreads(1) --- ref(<weakref at 0x000001EED4C2B220; dead>)
[step](22): workThreads(0) --- ref(<weakref at 0x000001EED4C2B220; dead>)
"""