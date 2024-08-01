# Name: BBS任务分片调度服务
# Date: 2024-07-16
# Author: Ais
# Desc: None


import uvicorn
from fastapi import FastAPI


# 全量任务列表
TASKS = [f'0000{i}' for i in range(1, 10)]
# 任务分片大小
TASK_PART_SIZE = 3
# 任务分片集
TASKS_PART = [TASKS[i:i+TASK_PART_SIZE] for i in range(0, len(TASKS), TASK_PART_SIZE)]


app = FastAPI()

@app.get("/")
def home_page():
    return "BBS任务分片调度服务"

@app.get("/task/part/{part_id}")
def get_task(part_id:int):
    """获取分片任务数据"""
    if not (0 <= part_id < len(TASKS_PART)):
        return {"state": False, "tasks": [], "msg": f'part_id must be in [0, {len(TASKS_PART)-1}]'}
    return {"state": True, "tasks": TASKS_PART[part_id], "msg": "success"}


if __name__ == '__main__':
    uvicorn.run("bbs_task_service:app", host="127.0.0.1", port=8081) 