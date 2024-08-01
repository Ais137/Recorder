# Name: 论坛数据采集器(基类)
# Date: 2024-07-24
# Author: Ais
# Desc: None


import scrapy
from demo.items import PostMeta, PostData


class BBSCollectorBase(object):

    def collect_post_meta(self, response):
        """迭代列表页，采集帖子元数据"""
        for data in response.json().get("data") or []:
            # 解析帖子元数据
            post_meta = PostMeta(**data)
            yield post_meta
            self.logger.info(f'[{self.name}]({data["forum_id"]}): post({data["post_id"]}, {data["post_publish_time"]})')
            # 构造帖子详细接口请求
            # yield scrapy.Request(
            #     url = f'http://BBS/post/{data["post_id"]}',
            #     callback = self.collect_post_data,
            #     errback = self.collect_error,
            #     dont_filter = True, 
            # )
        # 迭代列表页
        response.meta["page"] += 1
        if response.meta["page"] <= response.meta["max_page"]:
            self.logger.info(f'[{self.name}]({response.meta["forum_id"]}): page({response.meta["page"]})')
            yield scrapy.Request(
                url = f'http://BBS/list/{response.meta["forum_id"]}/{response.meta["page"]}',
                meta = response.meta,
                callback = self.collect_post_meta,
                errback = self.collect_error,
                dont_filter = True,
            )

    def collect_post_data(self, response):
        """采集帖子详细数据"""
        data = response.json()
        post_data = PostData(
            post_id = data["post_id"],
            post_publish_time = data["post_publish_time"],
            post_publish_userid = data["post_publish_userid"],
            post_content = data["post_content"],
            post_comment_count = data["post_comment_count"],
            post_comments = [],
        )
        # 构造评论接口请求
        if post_data["post_comment_count"] == 0:
            yield post_data
        else:
            yield scrapy.Request(
                url = f'https://BBS/comment/{post_data["post_id"]}/{1}',
                meta = {
                    "post_data": post_data,
                    "page": 1,
                },
                callback = self.collect_post_comment,
                errback =  self.collect_error,
                dont_filter = True,  
            )

    def collect_post_comment(self, response):
        """采集帖子评论数据"""
        data = response.json()
        post_data = response.meta["post_data"]
        for comment in data.get("comments") or []:
            post_data["post_comments"].append({
                "comment_id": comment["comment_id"],
                "comment_publish_time": comment["comment_publish_time"],
                "comment_publish_user": comment["comment_publish_user"],
                "comment_content": comment["comment_content"],
            })
        if data["end"]:
            yield post_data
        else:
            page = response.meta["page"] + 1
            yield scrapy.Request(
                url = f'https://BBS/comment/{post_data["post_id"]}/{page}',
                meta = {
                    "post_data": post_data,
                    "page": page,
                },
                callback = self.collect_post_comment,
                errback =  self.collect_error,
                dont_filter = True,  
            ) 

    def collect_error(self, failure):
        """异常处理"""
        print(failure)