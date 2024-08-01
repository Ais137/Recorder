# Name: BBS数据接口服务
# Date: 2024-07-16
# Author: Ais
# Desc: None


import time
import uvicorn
import sqlite3
import traceback
from fastapi import FastAPI


# 请求延迟配置
REQUEST_DELAY = 1


# 连接数据库
bbs_database = sqlite3.connect("./bbs.db", check_same_thread=False)


app = FastAPI()


@app.get("/")
def home_page():
    return "BBS数据接口服务"

@app.get("/list/{forum_id}/{page}")
def post_list(forum_id:str, page:int, page_size:int=20):
    """列表数据接口
    
    Args:
        * forum_id: 论坛id
        * page: 页数
        * page_size: 分页大小
    
    Returns:
        数据字段(data)定义如下:
        [
            {
                "forum_id": "论坛id",
                "post_id": "帖子id",
                "post_publish_time": "帖子发布时间",
                "post_publish_userid": "帖子发布者id",
            }
        ]

    """
    try:
        time.sleep(REQUEST_DELAY)
        cursor = bbs_database.cursor()
        datas = cursor.execute(f'SELECT * FROM posts WHERE forum_id="{forum_id}" ORDER BY post_publish_time DESC LIMIT {page_size} OFFSET {page*page_size};')
        posts_data_key = ("forum_id", "post_id", "post_publish_time", "post_publish_userid")
        posts = [dict(zip(posts_data_key, data)) for data in datas]
        return {"state": True, "data": posts}
    except: 
        print(traceback.format_exc())
        return {"state": False, "data": []}

def post_data():
    """帖子数据接口"""
    pass

def post_comment():
    """评论数据接口"""
    pass


if __name__ == '__main__':
    uvicorn.run("bbs_data_service:app", host="127.0.0.1", port=8080) 