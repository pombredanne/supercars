#!/usr/bin/env python

"""
This is a demo REST server. Do not use this in production!
"""

import time
import BaseHTTPServer
import SimpleHTTPServer
import urlparse
import json
from pymongo import Connection
from pymongo.objectid import ObjectId

__version__ = "0.1"
SERVER_HOST  = 'localhost'
SERVER_PORT  = 8000
SERVER_APIPREFIX = 'rest'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017


#class RestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
class RestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # add a mongodb connection to the RequestHandler
        self.mongoconn = Connection(MONGODB_HOST, MONGODB_PORT)
        self.server_version = "restserver/" + __version__
        #BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if path_elements[0] != SERVER_APIPREFIX:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        elif len(path_elements) == 3:
            api, database, table = path_elements
            #query = url.query
            db = self.mongoconn[database]
            result = db[table].find()
            self.do_HEAD()
            self.wfile.write('[')
            for i, r in enumerate(result):
                if i != 0:
                    self.wfile.write(',')
                r['_id'] = str(r['_id'])
                self.wfile.write(json.dumps(r))
            self.wfile.write(']')
        elif len(path_elements) == 4:
            api, database, table, oid = path_elements
            db = self.mongoconn[database]
            result = db[table].find_one({'_id': ObjectId(oid)})
            self.do_HEAD()
            if result:
                result['_id'] = str(result['_id'])
                self.wfile.write(json.dumps(result))
        else:
            self.send_error(404,
                'Use existing /%s/database/table/_id for document access'
                    % SERVER_APIPREFIX)

    def do_POST(self):
        """Respond to a POST request."""
        # Example (using cURL):
        # curl -X POST -d '{"name":"BODEGA LURTON","year":"2011","grapes":"Pinot Gris","country":"Argentina","region":"Mendoza","description":"Solid notes of black currant blended with a light citrus make this wine an easy pour for varied palates."}' 'http://localhost:9009/cellar/wines/'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if len(path_elements) == 3:
            api, database, table = path_elements
            content_len = int(self.headers.getheader('content-length'))
            try:
                data = json.loads(self.rfile.read(content_len))
                if data:
                    db = self.mongoconn[database]
                    oid = db[table].insert(data)
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
        # curl -X PUT -d '{"name":"CHATEAU DE SAINT COSME","year":"2009","grapes":"Grenache / Syrah","country":"France","region":"Southern Rhone / Gigondas","description":"The aromas of fruit and spice give one a hint of the light drinkability of this lovely wine, which makes an excellent complement to fish dishes."}' 'http://localhost:9009/cellar/wines/4fb8ad99b0ab584586000000'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if len(path_elements) == 4:
            api, database, table, oid = path_elements
            content_len = int(self.headers.getheader('content-length'))
            try:
                data = json.loads(self.rfile.read(content_len))
                if data:
                    db = self.mongoconn[database]
                    db[table].update({'_id': ObjectId(oid)}, data)
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
        # curl -X DELETE 'http://localhost:9009/cellar/wines/4fb8a590b0ab582e8e000001'

        url = urlparse.urlparse(self.path)
        path_elements = url.path.strip('/').split('/')
        if len(path_elements) == 4:
            api, database, table, oid = path_elements
            db = self.mongoconn[database]
            result = db[table].remove(ObjectId(oid))
            self.do_HEAD()
            if result:
                self.wfile.write(result)
        else:
            self.send_error(404,
                'Use existing /%s/database/table/_id/ to delete documents'
                    % SERVER_APIPREFIX)


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((SERVER_HOST, SERVER_PORT), RestHandler)
    print time.asctime(), "Server Starts - %s:%s" % (SERVER_HOST, SERVER_PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (SERVER_HOST, SERVER_PORT)
