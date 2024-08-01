# Name: scrapy-redis任务推送器
# Date: 2024-07-17
# Author: Ais
# Desc: None


import json
import redis


# redis连接参数
REDIS_PARAMS = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0,
    "password": "",
}

# 任务列表
TASKS = [{"forum_id": f'0000{i}'} for i in range(1, 10)]
# 任务队列键名
redis_key = "BBSCollector.taskqueue"

# 推送任务数据到 redis 任务队列
client = redis.Redis(**REDIS_PARAMS)
[client.rpush(redis_key, json.dumps(task)) for task in TASKS]


