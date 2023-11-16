# Scrapy settings for demo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'demo'

SPIDER_MODULES = ['demo.spiders']
NEWSPIDER_MODULE = 'demo.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

HTTPERROR_ALLOW_ALL = True

LOG_LEVEL = 'INFO'

# 启用扩展组件
EXTENSIONS = {
   'demo.extensions.statsuploader.StatsUploader': 300,
}

# 设置上传模式
STATSUPLOADER_UPLOAD_MODE = "UPLOAD_INTERVAL"

# 设置连接配置
STATSUPLOADER_CONNECT_CONFS = {
    "key": "test.collectors.stats",
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0,
}

# 设置上传时间间隔
STATSUPLOADER_UPLOAD_INTERVAL = 10
