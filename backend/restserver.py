#!/usr/bin/env python

"""
This is a demo REST server. Do not use this in production!
"""

import time
import BaseHTTPServer
import SimpleHTTPServer
import urlparse
import json
import os
import sys


here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))

__version__ = "0.1"
SERVER_HOST = 'localhost'
SERVER_PORT = 8000
SERVER_APIPREFIX = 'rest'
WINECELLAR_FILE = here('winecellar.json')


#class RestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
class RestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    wines = {}  # store the wines
    conf = {'seq': 1}  # unique id for the next wine entry

    def __init__(self, *args, **kwargs):
        if not self.wines:
            self.load_wines(WINECELLAR_FILE)
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        # Example (using cURL):
        # curl -X GET 'http://localhost:8000/rest/cellar/wines/'
        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[0] != SERVER_APIPREFIX:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        elif path_elements[1] != 'cellar' or path_elements[2] != 'wines':
            self.send_error(404,
                'Use existing /%s/database/table/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 3:
            api, database, table = path_elements
            self.do_HEAD()
            self.wfile.write('[')
            for i, r in enumerate(self.wines):
                if i != 0:
                    self.wfile.write(',')
                self.wfile.write(json.dumps(self.wines[r]))
            self.wfile.write(']')
        elif len(path_elements) == 4:
            api, database, table, oid = path_elements
            try:
                result = self.wines[oid]
                self.do_HEAD()
                if result:
                    #result['_id'] = str(result['_id'])
                    self.wfile.write(json.dumps(result))
            except KeyError:
                self.send_error(404, 'Invalid record id')
        else:
            self.send_error(404,
                'Use existing /%s/database/table/_id for document access'
                    % SERVER_APIPREFIX)

    def do_POST(self):
        """Respond to a POST request."""
        # Example (using cURL):
        # curl -X POST -d '{"name":"BODEGA LURTON","year":"2011","grapes":"Pinot Gris","country":"Argentina","region":"Mendoza","description":"Solid notes of black currant blended with a light citrus make this wine an easy pour for varied palates."}' 'http://localhost:8000/rest/cellar/wines/'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[1] != 'cellar' or path_elements[2] != 'wines':
            self.send_error(404,
                'Use existing /%s/database/table/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 3:
            api, database, table = path_elements
            content_len = int(self.headers.getheader('content-length'))
            try:
                data = json.loads(self.rfile.read(content_len))
                if data:
                    oid = self.next_id()
                    data['_id'] = oid
                    self.wines[oid] = data
                    self.do_HEAD()
                    if oid:
                        self.wfile.write('{"_id": "%s"}' % oid)
                else:
                    self.send_error(400, 'No data received')
            except ValueError:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404,
                'Use existing /%s/database/table/ to create documents'
                    % SERVER_APIPREFIX)

    def do_PUT(self):
        """Respond to a PUT request."""
        # Example (using cURL):
        # curl -X PUT -d '{"name":"CHATEAU DE SAINT COSME","year":"2009","grapes":"Grenache / Syrah","country":"France","region":"Southern Rhone / Gigondas","description":"The aromas of fruit and spice give one a hint of the light drinkability of this lovely wine, which makes an excellent complement to fish dishes."}' 'http://localhost:8000/rest/cellar/wines/4fb8ad99b0ab584586000000'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[1] != 'cellar' or path_elements[2] != 'wines':
            self.send_error(404,
                'Use existing /%s/database/table/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 4:
            api, database, table, oid = path_elements
            content_len = int(self.headers.getheader('content-length'))
            try:
                data = json.loads(self.rfile.read(content_len))
                if data:
                    data['_id'] = oid
                    self.wines[oid] = data
                    self.do_HEAD()
            except ValueError:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404,
                'Use existing /%s/database/table/_id/ for updating a document'
                    % SERVER_APIPREFIX)

    def do_DELETE(self):
        """Respond to a DELETE request."""
        # Example (using cURL):
        # curl -X DELETE 'http://localhost:8000/rest/cellar/wines/4fb8a590b0ab582e8e000001'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[1] != 'cellar' or path_elements[2] != 'wines':
            self.send_error(404,
                'Use existing /%s/database/table/_id for document access'
                    % SERVER_APIPREFIX)
        elif len(path_elements) == 4:
            api, database, table, oid = path_elements
            if oid in self.wines:
                self.wines.pop(oid)
                self.do_HEAD()
            else:
                self.send_error(404,
                    'record does not exist')
        else:
            self.send_error(404,
                'Use existing /%s/database/table/_id/ to delete documents'
                    % SERVER_APIPREFIX)

    def log_message(self, format, *args):
        # shut up!
        pass

    def next_id(self):
        """Create a unique record id"""
        res = "%0.5d" % self.conf['seq']
        self.conf['seq'] += 1
        return res

    def load_wines(self, filename):
        """Load wine cellar from json file"""
        f = open(filename)
        data = json.loads("".join(f.readlines()))
        f.close()
        for d in data:
            oid = self.next_id()
            d['_id'] = oid
            self.wines[oid] = d


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((SERVER_HOST, SERVER_PORT), RestHandler)
    print time.asctime(), "Server Starts - %s:%s" % (SERVER_HOST, SERVER_PORT)
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (SERVER_HOST, SERVER_PORT)
