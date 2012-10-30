import sys
import logging
import json


from nose.tools import assert_equal, assert_true
from mock import MagicMock

from testutils import HttpServerTestBase

sys.path.append("../../backend")
from restserver import RestHandler

logger = logging.getLogger(__name__)


class TestPutMethod(HttpServerTestBase):
    def setUp(self):
        self.request_handler = RestHandler
        HttpServerTestBase.setUp(self)

        def no_output(self, *args, **kwargs):
            pass

        # prepare mock
        self.thread.server.do_HEAD = MagicMock()
        self.thread.server.send_error = MagicMock()

    def test_put_changed_record(self):
        new_record = '{"name":"AC COBRA","country":"United States","top_speed":"160","0-60":"4.2","power":"485","engine":"6997","weight":"1148","description":"The AC Cobra, sold as the Ford/Shelby AC Cobra in the USA and often known colloquially as the Shelby Cobra in that country, is an American-engined British sports car produced intermittently since 1962.","image":"005.png"}'

        response = self.request(
            'http://localhost/rest/supercars/00001',
            method="PUT", body=new_record)
        try:
            assert_equal(response.read(), '')
            self.thread.server.do_HEAD.assert_called_once()
            # verify changes are visible in GET request
            response = self.request(
            "http://localhost/rest/supercars/00001",
            method="GET")
            expected = json.loads(new_record)
            expected['_id'] = '00001'
            assert_equal(json.loads(response.read()), expected)
        finally:
            response.close()


    def test_get_invalid_path(self):
        response = self.request(
            'http://localhost/something/else',
            method="PUT", body='something here')
        try:
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: Use existing /rest/supercars/_id for document access.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
            self.thread.server.do_HEAD.assert_called_once()
            self.thread.server.send_error.assert_called_once()
        finally:
            response.close()
