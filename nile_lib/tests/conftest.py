import pytest
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import time


def pytest_configure():
    """
    This function is here so that locust is imported as soon as possible

    This aims to prevent issues related to monkey patching
    when monkey patching occurds after ssl has been imported
    issues can occur see:

    https://github.com/gevent/gevent/issues/1016
    """
    import locust  # noqa: F401


@pytest.fixture()
def echo_server():
    """
    A Fixture that creates a basic Echo Server
    which responds 200 to GET, POST, and DELETE messages
    """
    def _run_server(server):
        server.serve_forever()

    server = HTTPServer(('localhost', 8000), EchoRequestHandler)
    server_thread = threading.Thread(target=_run_server, args=(server,))
    server_thread.start()
    yield server
    server.shutdown()
    server.server_close()
    server_thread.join()


class EchoRequestHandler(BaseHTTPRequestHandler):
    """A simple Echo server"""
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

    def do_DELETE(self):
        print(f"{time.ctime()}: DELETE Received")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(self.path, "utf-8"))
