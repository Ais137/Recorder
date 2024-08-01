# Name: 数据容器
# Date: 2024-07-16
# Author: Ais
# Desc: None


import scrapy


class PostMeta(scrapy.Item):
    """帖子元数据容器"""
    # 论坛id
    forum_id = scrapy.Field()
    # 帖子id
    post_id = scrapy.Field()
    # 帖子发布时间
    post_publish_time = scrapy.Field()
    # 帖子发布者id
    post_publish_userid = scrapy.Field()


class PostData(scrapy.Item):
    """帖子详细数据容器"""
    # 帖子id
    post_id = scrapy.Field()
    # 帖子发布时间
    post_publish_time = scrapy.Field()
    # 帖子发布者id
    post_publish_userid = scrapy.Field()
    # 帖子标题
    post_title = scrapy.Field()
    # 帖子正文
    post_content = scrapy.Field()
    # 帖子评论数量
    post_comment_count = scrapy.Field()