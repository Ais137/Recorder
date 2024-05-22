# Name: test_func_timeout
# Date: 2024-04-24
# Author: Ais
# Desc: 研究利用信号机制实现的函数调用超时方案


import time
import signal


def timeout(timeout_sec):
    def timeout_decorater(func):
        def timeout_handler(signum, frame):
            raise TimeoutError()
        def timeout_func(*args, **kwargs):
            # 设置信号处理函数
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_sec)
            # 调用目标函数
            result = func(*args, **kwargs)
            signal.alarm(0)
            return result
        return timeout_func
    return timeout_decorater


if __name__ ==  "__main__":
    
    @timeout(5)
    def test(t):
        time.sleep(t)
        print(f'test({t})')

    test(3)
    test(4)
    test(5)

    """
    test(3)
    test(4)
    Traceback (most recent call last):
        File "/root/src/concurrent_performance/test_timeout.py", line 36, in <module>
            test(5)
        File "/root/src/concurrent_performance/test_timeout.py", line 20, in timeout_func
            result = func(*args, **kwargs)
                    ^^^^^^^^^^^^^^^^^^^^^
        File "/root/src/concurrent_performance/test_timeout.py", line 31, in test
            time.sleep(t)
        File "/root/src/concurrent_performance/test_timeout.py", line 14, in timeout_handler
            raise TimeoutError()
    TimeoutError
    """