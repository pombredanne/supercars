import logging
import json
import BaseHTTPServer

from nose.tools import assert_equal, assert_true
from mock import MagicMock

from restserver import RestHandler
from testutils import HttpServerTestBase

logger = logging.getLogger(__name__)

SERVER_HOST = 'localhost'
SERVER_PORT = 8000


class TestGetMethod(HttpServerTestBase):
    def setUp(self):
        self.request_handler = RestHandler
        HttpServerTestBase.setUp(self)

        # prepare mock
        self.thread.server.do_HEAD = MagicMock()

    def test_get_one_record(self):
        response = self.request(
            "http://localhost:8000/rest/cellar/wines/00001",
            method="GET")
        expected = {"_id": "00001", "name": "BLOCK NINE", "year": "2009", "grapes": "Pinot Noir", "country": "USA", "region": "California", "description": "With hints of ginger and spice, this wine makes an excellent complement to light appetizer and dessert fare for a holiday gathering.", "image": "block_nine.jpg"}
        try:
            assert_equal(expected, json.loads(response.read()))
            self.thread.server.do_HEAD.assert_called_once()
        finally:
            response.close()
