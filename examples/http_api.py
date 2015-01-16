__author__ = 'Samuel Marks <samuelmarks@gmail.com>'
__version__ = '0.1.0'

from SocketServer import ThreadingTCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from webbrowser import open_new_tab
from json import dumps
from urlparse import urlparse
from os import environ
from types import NoneType

from linkedin.linkedin import LinkedInAuthentication, LinkedInApplication, PERMISSIONS

PORT = 8080


class LinkedInWrapper(object):
    """ Simple namespacing """
    API_KEY = environ.get('LINKEDIN_API_KEY')
    API_SECRET = environ.get('LINKEDIN_API_SECRET')
    RETURN_URL = 'http://localhost:{0}/code'.format(globals()['PORT'])
    authentication = LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL, PERMISSIONS.enums.values())
    application = LinkedInApplication(authentication)


liw = LinkedInWrapper()
run_already = False
params_to_d = lambda params: {
    l[0]: l[1] for l in map(lambda j: j.split('='), urlparse(params).query.split('&'))
}


class CustomHandler(SimpleHTTPRequestHandler):
    def json_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        parsedurl = urlparse(self.path)
        authed = type(liw.authentication.token) is not NoneType

        if parsedurl.path == '/code':
            self.json_headers()

            liw.authentication.authorization_code = params_to_d(self.path).get('code')
            self.wfile.write(dumps({'access_token': liw.authentication.get_access_token(),
                                    'routes': filter(lambda d: not d.startswith('_'), dir(liw.application))}))
        elif parsedurl.path == '/routes':
            self.json_headers()

            self.wfile.write(dumps({'routes': filter(lambda d: not d.startswith('_'), dir(liw.application))}))
        elif not authed:
            self.json_headers()

            if not globals()['run_already']:
                open_new_tab(liw.authentication.authorization_url)
            globals()['run_already'] = True
            self.wfile.write(dumps({'path': self.path, 'authed': type(liw.authentication.token) is NoneType}))
        elif authed and len(parsedurl.path) and parsedurl.path[1:] in dir(liw.application):
            self.json_headers()
            self.wfile.write(dumps(getattr(liw.application, parsedurl.path[1:])()))
        else:
            self.json_headers(501)
            self.wfile.write(dumps({'error': 'NotImplemented'}))


if __name__ == '__main__':
    httpd = ThreadingTCPServer(('localhost', PORT), CustomHandler)

    print 'Server started on port:', PORT
    httpd.serve_forever()
