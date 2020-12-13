from __future__ import print_function

try:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except ImportError:
    from http.server import SimpleHTTPRequestHandler    # type: ignore

try:
    import SocketServer as socketserver
except ImportError:
    import socketserver     # type: ignore

import logging
import cgi

PORT = 8080


class ServerHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.error(self.headers)
        # FIXME: This super() call is incompatible with Python 2.7
        super().do_GET()

    def do_POST(self):
        logging.error(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        for item in form.list:
            logging.error(item)
        # FIXME: This super() call is incompatible with Python 2.7
        super().do_GET()


Handler = ServerHandler

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
