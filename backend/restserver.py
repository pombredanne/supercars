#!/usr/bin/env python

"""
This is a demo REST server. Do not use this in production!
"""

import time
import BaseHTTPServer
import SocketServer
import SimpleHTTPServer
import urlparse
import json
import os
import sys
from collections import OrderedDict


here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))

__version__ = "0.1.1"
SERVER_HOST = '0.0.0.0'
SERVER_APIPREFIX = 'rest'
SUPERCARS_FILE = here('supercars.json')


class RestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    supercars = OrderedDict()  # store the supercars
    conf = {'seq': 1}  # unique id for the next supercar entry

    def __init__(self, *args, **kwargs):
        if not(len(self.supercars)):
            self.load_supercars(SUPERCARS_FILE)
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        # Example (using cURL):
        # curl -X GET 'http://localhost:8000/rest/supercars/'
        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        # print 'path_elements: %s' % path_elements
        if path_elements[0] != SERVER_APIPREFIX:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        elif path_elements[1] != 'supercars':
            self.send_error(404,
                'Use existing /%s/supercars/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 2:
            api, table = path_elements
            self.do_HEAD()
            self.wfile.write('[')
            for i, r in enumerate(self.supercars):
                if i != 0:
                    self.wfile.write(',')
                self.wfile.write(json.dumps(self.supercars[r]))
            self.wfile.write(']')
        elif len(path_elements) == 3:
            api, table, oid = path_elements
            try:
                result = self.supercars[oid]
                self.do_HEAD()
                if result:
                    #result['_id'] = str(result['_id'])
                    self.wfile.write(json.dumps(result))
            except KeyError:
                self.send_error(404, 'Invalid record id')
        else:
            self.send_error(404,
                'Use existing /%s/supercars/_id for document access'
                    % SERVER_APIPREFIX)

    def do_POST(self):
        """Respond to a POST request."""
        # Example (using cURL):
        # curl -X POST -d '{"name":"Ferrari Enzo","country":"Italy","top_speed":"218","0-60":"3.4","power":"650","engine":"5998","weight":"1365","description":"The Enzo Ferrari is a 12 cylinder mid-engine berlinetta named after the company\"s founder, Enzo Ferrari.","image":"050.png"}' 'http://localhost:8000/rest/supercars/'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        # print 'path_elements: %s' % path_elements
        if path_elements[1] != 'supercars':
            self.send_error(404,
                'Use existing /%s/supercars/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 2:
            api, table = path_elements
            content_len = int(self.headers.getheader('content-length'))
            try:
                data = json.loads(self.rfile.read(content_len))
                if data:
                    oid = self.next_id()
                    data['_id'] = oid
                    self.supercars[oid] = data
                    self.do_HEAD()
                    if oid:
                        self.wfile.write('{"_id": "%s"}' % oid)
                else:
                    self.send_error(400, 'No data received')
            except ValueError:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404,
                'Use existing /%s/supercars/ to create documents'
                    % SERVER_APIPREFIX)

    def do_PUT(self):
        """Respond to a PUT request."""
        # Example (using cURL):
        # curl -X PUT -d '{TODO}' 'http://localhost:8000/rest/supercars/4fb8ad99b0ab584586000000'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[1] != 'supercars':
            self.send_error(404,
                'Use existing /%s/supercars/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 3:
            api, table, oid = path_elements
            content_len = int(self.headers.getheader('content-length'))
            try:
                data = json.loads(self.rfile.read(content_len))
                if data:
                    data['_id'] = oid
                    self.supercars[oid] = data
                    self.do_HEAD()
            except ValueError:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404,
                'Use existing /%s/supercars/_id/ for updating a document'
                    % SERVER_APIPREFIX)

    def do_DELETE(self):
        """Respond to a DELETE request."""
        # Example (using cURL):
        # curl -X DELETE 'http://localhost:8000/rest/supercars/4fb8a590b0ab582e8e000001'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[1] != 'supercars':
            self.send_error(404,
                'Use existing /%s/supercars/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 3:
            api, table, oid = path_elements
            if oid in self.supercars:
                self.supercars.pop(oid)
                self.do_HEAD()
            else:
                self.send_error(404,
                    'record does not exist')
        else:
            self.send_error(404,
                'Use existing /%s/supercars/_id/ to delete documents'
                    % SERVER_APIPREFIX)

    def log_message(self, format, *args):
        # shut up!
        pass

    def next_id(self):
        """Create a unique record id"""
        res = "%0.5d" % self.conf['seq']
        self.conf['seq'] += 1
        return res

    def load_supercars(self, filename):
        """Load supercars from json file"""
        f = open(filename)
        data = json.loads("".join(f.readlines()))
        f.close()
        for d in data:
            oid = self.next_id()
            d['_id'] = oid
            self.supercars[oid] = d


class SimpleThreadedServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):
    pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "You need to provide a port number as 1st argument such as 8000!"
    httpd = SimpleThreadedServer((SERVER_HOST, int(sys.argv[1])), RestHandler)
    print time.asctime(), "Server Starts - %s:%s" % (SERVER_HOST, sys.argv[1])
    if len(sys.argv) > 2:
        os.chdir(sys.argv[2])
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (SERVER_HOST, sys.argv[1])
