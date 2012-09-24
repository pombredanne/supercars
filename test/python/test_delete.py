import sys
import logging
import json

from nose.tools import assert_equal, assert_true
from mock import MagicMock

from testutils import HttpServerTestBase

sys.path.append("../../backend")
from restserver import RestHandler

logger = logging.getLogger(__name__)


class TestDeleteMethod(HttpServerTestBase):
    def setUp(self):
        self.request_handler = RestHandler
        HttpServerTestBase.setUp(self)

        def no_output(self, *args, **kwargs):
            pass

        # prepare mock
        self.thread.server.do_HEAD = MagicMock()
        self.thread.server.send_error = MagicMock()

    def test_delete_record(self):
        response = self.request(
            'http://localhost/rest/cellar/wines/00002',
            method="DELETE")
        try:
            assert_equal(response.read(), '')
            self.thread.server.do_HEAD.assert_called_once()
            # verify changes are visible in GET request
            response = self.request(
            "http://localhost/rest/cellar/wines/00002",
            method="GET")
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: Invalid record id.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
        finally:
            response.close()

    def test_delete_non_existant(self):
        response = self.request(
            'http://localhost/rest/cellar/wines/00050',
            method="DELETE")
        try:
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: record does not exist.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
            self.thread.server.do_HEAD.assert_called_once()
        finally:
            response.close()

    def test_delete_invalid_path(self):
        response = self.request(
            'http://localhost/something/else',
            method="DELETE")
        try:
            assert_equal(response.read(), '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code 404.\n<p>Message: Use existing /rest/database/table/_id for document access.\n<p>Error code explanation: 404 = Nothing matches the given URI.\n</body>\n')
            self.thread.server.do_HEAD.assert_called_once()
            self.thread.server.send_error.assert_called_once()
        finally:
            response.close()
