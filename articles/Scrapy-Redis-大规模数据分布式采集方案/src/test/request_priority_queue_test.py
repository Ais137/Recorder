# Name: 请求优先级队列测试
# Date: 2024-07-22
# Author: Ais
# Desc: None


import redis
from scrapy import Request, Spider
from scrapy_redis.queue import PriorityQueue
from scrapy_redis.defaults import SCHEDULER_QUEUE_KEY


# 构建请求队列实例
queue = PriorityQueue(
    server = redis.Redis(password="test123?"),
    spider = Spider(name="request_priority_queue_test"),
    key = SCHEDULER_QUEUE_KEY,
)

# 请求排队
print("[PriorityQueue]: enqueue_request")
reqs = [
    ("url://test/1", 10),
    ("url://test/2", 20),
    ("url://test/3", 10),
    ("url://test/4", 20),
    ("url://test/5", 30),
]
for url, priority in reqs:
    print(url, priority)
    queue.push(Request(url=url, priority=priority))

# 请求出队
print("[PriorityQueue]: next_request")
while queue:
    req = queue.pop()
    print(req.url, req.priority)

