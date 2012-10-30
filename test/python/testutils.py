#!/usr/bin/env python

import threading
import httplib
from BaseHTTPServer import HTTPServer

# code from Lib/test/test_httpservers.py


class TestServerThread(threading.Thread):
    def __init__(self, test_object, request_handler):
        threading.Thread.__init__(self)
        self.request_handler = request_handler
        self.test_object = test_object
        self.test_object.lock.acquire()


    def run(self):
        self.server = HTTPServer(('', 0), self.request_handler)
        self.test_object.PORT = self.server.socket.getsockname()[1]
        self.test_object.lock.release()
        try:
            self.server.serve_forever()
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()


class HttpServerTestBase:
    def setUp(self):
        self.lock = threading.Lock()
        self.thread = TestServerThread(self, self.request_handler)
        self.thread.start()
        self.lock.acquire()

    def tearDown(self):
        self.lock.release()
        self.thread.stop()

    def request(self, uri, method='GET', body=None, headers={}):
        self.connection = httplib.HTTPConnection('localhost', self.PORT)
        self.connection.request(method, uri, body, headers)
        return self.connection.getresponse()
