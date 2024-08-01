# Name: Prometheus exporter
# Date: 2024-07-29
# Author: Ais
# Desc: None


import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from collector_monitor import CollectorMonitor


monitor = CollectorMonitor(
    service_name = "BBS",
    spider_name = "BBSCollector-scrapy-redis",
    redis_params =  {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0,
        "password": "",
    },
    redis_keys = {
        "task_queue": "BBSCollector.taskqueue"
    }
)

app = FastAPI()

@app.get("/")
def home_page():
    return "采集服务监控"

@app.get("/metrics")
def collector_monitor():
    return HTMLResponse(
        content = monitor.metrics()
    )



if __name__ ==  "__main__":
    uvicorn.run("collector_exporter:app", host="0.0.0.0", port=8088) 
