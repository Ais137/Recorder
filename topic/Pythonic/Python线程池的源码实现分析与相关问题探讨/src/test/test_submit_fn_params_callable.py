# Name: test_submit_fn_params_callable
# Date: 2024-04-18
# Author: Ais
# Desc: 测试 submit 方法的 目标函数(fn) 使用 可调用对象 的应用场景。


import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


URLS = [
    'https://www.google.com/',
    'https://www.python.org/',
    'https://github.com/',
    'https://www.kaggle.com/',
]


class Task(object):

    def __init__(self, url, timeout) -> None:
        self.url = url
        self.timeout = (timeout, timeout) if isinstance(timeout, int) else timeout
        self.res = None
        self.start = None
        self.end = None

    def __call__(self):
        self.start = time.time()
        self.res = requests.get(
            url = self.url, 
            timeout = self.timeout,
        )
        self.end = time.time()
        return self


with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(Task(url, 30)) for url in URLS]
    for future in as_completed(futures):
        task = future.result()
        print(f'[task]({task.res.status_code}): start({task.start}) -> end({task.end}) -> url({task.url})')
    

"""
# OUTPUT
[task](200): start(1713433712.8698785) -> end(1713433713.3096645) -> url(https://www.google.com/)
[task](200): start(1713433712.8708787) -> end(1713433713.3628254) -> url(https://github.com/)
[task](200): start(1713433713.3096645) -> end(1713433714.4990556) -> url(https://www.kaggle.com/)
[task](200): start(1713433712.8698785) -> end(1713433718.296104) -> url(https://www.python.org/)
"""