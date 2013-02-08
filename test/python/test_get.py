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

        self.maxDiff = None

    def test_get_one_record(self):
        response = self.request(
            "http://localhost/rest/supercars/00001",
            method="GET")
        expected = {u'engine': u'6997', u'top_speed': u'160', u'name': u'AC Cobra', u'power': u'485', u'country': u'United States', u'image': u'005.png', u'weight': u'1148', u'zero_to_sixty': u'4.2', '_id': '00001', u'description': u'The AC Cobra, sold as the Ford/Shelby AC Cobra in the USA and often known colloquially as the Shelby Cobra in that country, is an American-engined British sports car produced intermittently since 1962.'}
        try:
            assert_equal(json.loads(response.read()), expected)
            self.thread.server.do_HEAD.assert_called_once()
        finally:
            response.close()

    def test_get_list_of_records(self):
        response = self.request(
            "http://localhost/rest/supercars/",
            method="GET")
        try:
            supercars = json.loads(response.read())
            print supercars
            assert_equal(len(supercars), 30)
            assert_equal(supercars[0]['name'], 'AC Cobra')
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
