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
        new_record = '{"name":"VITICCIO CLASSICO RISERVA","year":"2007","grapes":"Sangiovese Merlot","country":"Italy","region":"Tuscany","description":"Though soft and rounded in texture, the body of this wine is full and rich and oh-so-appealing. This delivery is even more impressive when one takes note of the tender tannins that leave the taste buds wholly satisfied.","image":"viticcio.jpg"}'

        response = self.request(
            'http://localhost/rest/cellar/wines/',
            method="POST", body=new_record)
        try:
            assert_equal(response.read(), '{"_id": "00012"}')
            self.thread.server.do_HEAD.assert_called_once()
            # verify changes are visible in GET request
            response = self.request(
            "http://localhost/rest/cellar/wines/00012",
            method="GET")
            expected = json.loads(new_record)
            expected['_id'] = '00012'
            assert_equal(json.loads(response.read()), expected)
        finally:
            response.close()


    def test_get_invalid_path(self):
        response = self.request(
            'http://localhost/something/else',
            method="POST", body='something here')
        try:
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: Use existing /rest/database/table/_id for document access.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
            self.thread.server.do_HEAD.assert_called_once()
            self.thread.server.send_error.assert_called_once()
        finally:
            response.close()
