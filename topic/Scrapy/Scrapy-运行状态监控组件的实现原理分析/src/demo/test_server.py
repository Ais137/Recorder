# Name: 测试服务器
# Date: 2023-08-18
# Author: Ais
# Desc: None


import json
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        time.sleep(3)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"status": 0, "path": self.path}).encode("utf-8"))

server = ThreadingHTTPServer(('', 8000), HTTPRequestHandler)
server.serve_forever()

