# Name: 测试工作线程初始化失败
# Date: 2024-04-18
# Author: Ais
# Desc: 测试工作线程初始化失败导致submit提交新任务失败


from concurrent.futures import ThreadPoolExecutor, as_completed


def task(tid):
    print(f"[task]({tid}) completed")

def work_thread_initializer():
    raise Exception("test work_thread initializer failed")

with ThreadPoolExecutor(initializer=work_thread_initializer) as executor:
    [executor.submit(task, i) for i in range(10)]
    [executor.submit(task, i) for i in range(10, 20)]


"""
# OUTPUT
Traceback (most recent call last):
  File ".\test_initializer_failed.py", line 18, in <module>
    [executor.submit(task, i) for i in range(10, 20)]
  File ".\test_initializer_failed.py", line 18, in <listcomp>
    [executor.submit(task, i) for i in range(10, 20)]
  File "D:\Anaconda\lib\concurrent\futures\thread.py", line 176, in submit
    raise BrokenThreadPool(self._broken)
"""