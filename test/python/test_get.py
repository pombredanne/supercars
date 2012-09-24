import sys
import logging
import json
import BaseHTTPServer

from nose.tools import assert_equal, assert_true
from mock import MagicMock

from testutils import HttpServerTestBase

sys.path.append("../../backend")
from restserver import RestHandler

logger = logging.getLogger(__name__)

SERVER_HOST = 'localhost'
SERVER_PORT = 8000


class TestGetMethod(HttpServerTestBase):
    def setUp(self):
        self.request_handler = RestHandler
        HttpServerTestBase.setUp(self)

        def no_output(self, *args, **kwargs):
            pass

        # prepare mock
        self.thread.server.do_HEAD = MagicMock()
        self.thread.server.send_error = MagicMock()

    def test_get_one_record(self):
        response = self.request(
            "http://localhost/rest/cellar/wines/00001",
            method="GET")
        expected = {"_id": "00001", "name": "BLOCK NINE", "year": "2009", "grapes": "Pinot Noir", "country": "USA", "region": "California", "description": "With hints of ginger and spice, this wine makes an excellent complement to light appetizer and dessert fare for a holiday gathering.", "image": "block_nine.jpg"}
        try:
            assert_equal(json.loads(response.read()), expected)
            self.thread.server.do_HEAD.assert_called_once()
        finally:
            response.close()

    def test_get_list_of_records(self):
        response = self.request(
            "http://localhost/rest/cellar/wines",
            method="GET")
        try:
            wines = json.loads(response.read())
            print wines
            assert_equal(len(wines), 10)
            assert_equal(wines[0]['name'], 'OWEN ROE "EX UMBRIS"')
            self.thread.server.do_HEAD.assert_called_once()
        finally:
            response.close()

    def test_get_invalid_path(self):
        response = self.request(
            "http://localhost/something/else",
            method="GET")
        try:
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: File not found.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
            self.thread.server.do_HEAD.assert_called_once()
            self.thread.server.send_error.assert_called_once()
        finally:
            response.close()
