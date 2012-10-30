import sys
import logging
import json

from nose.tools import assert_equal, assert_true
from mock import MagicMock

from testutils import HttpServerTestBase

sys.path.append("../../backend")
from restserver import RestHandler

logger = logging.getLogger(__name__)


class TestPostMethod(HttpServerTestBase):
    def setUp(self):
        self.request_handler = RestHandler
        HttpServerTestBase.setUp(self)

        def no_output(self, *args, **kwargs):
            pass

        # prepare mock
        self.thread.server.do_HEAD = MagicMock()
        self.thread.server.send_error = MagicMock()

    def test_post_new_record(self):
        new_record = '''{"name":"Ferrari Enzo","country":"Italy","top_speed":"218","0-60":"3.4","power":"650","engine":"5998","weight":"1365","description":"The Enzo Ferrari is a 12 cylinder mid-engine berlinetta named after the company's founder, Enzo Ferrari.","image":"050.png"}'''

        response = self.request(
            'http://localhost/rest/supercars/',
            method="POST", body=new_record)
        try:
            assert_equal(response.read(), '{"_id": "00003"}')
            self.thread.server.do_HEAD.assert_called_once()
            # verify changes are visible in GET request
            response = self.request(
            "http://localhost/rest/supercars/00003",
            method="GET")
            expected = json.loads(new_record)
            expected['_id'] = '00003'
            assert_equal(json.loads(response.read()), expected)
        finally:
            response.close()


    def test_get_invalid_path(self):
        response = self.request(
            'http://localhost/something/else',
            method="POST", body='something here')
        try:
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: Use existing /rest/supercars/_id for document access.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
            self.thread.server.do_HEAD.assert_called_once()
            self.thread.server.send_error.assert_called_once()
        finally:
            response.close()
