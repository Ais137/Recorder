# 并发研究-python原生线程池的源码分析与内存占用问题

在使用 python 原生线程池来构建消费者并实现并发任务处理时。通常是采用以下方式。 

```py
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=5) as tp:
    tasks = [tp.submit(worker, (task)) for task in get_task(batch_size=5)]
    results = [future.result() for future in as_completed(tasks)]
```

通过 ```get_task(batch_size=5)``` 来获取任务，并通过 ```as_completed``` 来阻塞主进程，以等待子任务执行完成。

*as_completed* 在不同的使用场景下有不同的问题：

1. 如果子任务中存在耗时较长的任务，在启用 *as_completed* 且未设置 *timeout* 的情况下，主进程将阻塞在这个长耗时任务上，从而使系统的并发效率降低。

2. 在不使用 *as_completed* 或者 *timeout* 参数设置较低，导致主进程调用 *get_task* 获取任务的速度远远大于任务的执行速度时，由于原生线程池未实现 *拒绝策略* (线程池内部采用无限制队列)，会导致任务全部堆积到内存中，从而导致内存占用过高。

为了解决上述问题，通过分析 python原生线程池 的源码实现来探索解决方案。