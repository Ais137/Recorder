# Name: 定时任务调度
# Date: 2024-07-24
# Author: Ais
# Desc: None


import json
import time
import redis
import argparse


class BBSTaskScheduler(object):

    def __init__(self, redis_params:dict, redis_key:str):
        # 连接 redis 服务器
        self.redis_connect = redis.Redis(**redis_params)
        # 任务队列键名
        self.task_queue = redis_key

    def log(self, func, msg):
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))}][BBSTaskScheduler]({func}): {msg}')

    def push(self, task_ids:list) -> bool:
        """推送任务数据"""
        for tid in task_ids:
            task = {
                # 构建论坛id: 1 -> 00001
                "forum_id": f'{"0"*(5-len(str(tid)))}{tid}',
            }
            self.redis_connect.rpush(self.task_queue, json.dumps(task))
            self.log("push", task)
        return True
    
    def clean(self):
        """清除队列"""
        self.redis_connect.delete(self.task_queue)
        self.log("clean", "task queue cleaned")

    def len(self):
        """获取队列长度"""
        self.log("len", f"task_queue({self.redis_connect.llen(self.task_queue)})")


if __name__ ==  "__main__":

    # 构建调度器
    scheduler = BBSTaskScheduler(
        redis_params = {
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "password": "",
        },
        redis_key = "BBSCollector.taskqueue",
    )
    
    parser = argparse.ArgumentParser(prog='PROG', description="任务调度器")
    subparser = parser.add_subparsers(help="commands")

    # [push]: 推送任务
    command_push = subparser.add_parser(name="push", help="推送任务")
    command_push.add_argument("-t", "--task_ids", type=int, nargs="+", default=None, help="任务id列表")
    command_push.add_argument("-r", "--task_id_range", type=int, default=10, help="任务id范围列表(1, N)")
    command_push.add_argument("-l", "--loop", action="store_true", help="循环模式")
    command_push.add_argument("-i", "--interval", type=int, default=10, help="任务调度间隔(s)")
    def command_push_handler(args):
        # 任务id列表
        task_ids = args.task_ids if args.task_ids else list(range(1, args.task_id_range+1))
        if args.loop:
            while True:
                scheduler.push(task_ids)
                time.sleep(args.interval)
        else:
            scheduler.push(task_ids)
    command_push.set_defaults(func=command_push_handler)

    # [clean]: 清空任务
    command_clean = subparser.add_parser(name="clean", help="清空任务")
    def command_clean_handler(args):
        scheduler.clean() 
    command_clean.set_defaults(func=command_clean_handler)
   
    # [len]: 获取队列长度
    command_len = subparser.add_parser(name="len", help="获取队列长度")
    def command_len_handler(args):
        scheduler.len() 
    command_len.set_defaults(func=command_len_handler)

    args = parser.parse_args()
    args.func(args)
    


