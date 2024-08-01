# Name: 中间件
# Date: 2024-07-16
# Author: Ais
# Desc: None


from urllib.parse import urlparse


class BBSDomainMappingMiddleware(object):
    """域名映射中间件
    
    将 BBS 域名映射到 "127.0.0.1"
    """

    def process_request(self, request, spider):
        if urlparse(request.url).netloc == "bbs":
            return request.replace(url=request.url.replace("bbs", "127.0.0.1:8080", 1))