# Name: 测试服务器
# Date: 2023-08-18
# Author: Ais
# Desc: None


import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"status": 0, "path": self.path}).encode("utf-8"))

server = ThreadingHTTPServer(('', 8000), HTTPRequestHandler)
server.serve_forever()


import scrapy_redis