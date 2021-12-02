from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

import time


class EchoRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"{time.ctime()}: GET Received")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(self.path, "utf-8"))

    def do_POST(self):
        print(f"{time.ctime()}: POST Received")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())


if __name__ == "__main__":
    print("Creating Server")
    print("Will run indefinitely")
    httpd = HTTPServer(('localhost', 8000), EchoRequestHandler)
    httpd.serve_forever()
