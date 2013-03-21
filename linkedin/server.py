import BaseHTTPServer
import cgi

from .linkedin import LinkedInApplication, LinkedInAuthentication, PERMISSIONS


def quick_api(api_key, secret_key):
    """
    This method helps you get access to linkedin api quickly when using it
    from the interpreter.
    Notice that this method creates http server and wait for a request, so it
    shouldn't be used in real production code - it's just an helper for debugging

    The usage is basically:
    api = quick_api(KEY, SECRET)
    After you do that, it will print a URL to the screen which you must go in
    and allow the access, after you do that, the method will return with the api
    object.
    """
    auth = LinkedInAuthentication(api_key, secret_key, 'http://localhost:8000/',
                                  PERMISSIONS.enums.values())
    app = LinkedInApplication(authentication=auth)
    print auth.authorization_url
    _wait_for_user_to_enter_browser(app)
    return app


def _wait_for_user_to_enter_browser(app):
    class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(self):
            p = self.path.split('?')
            if len(p) > 1:
                params = cgi.parse_qs(p[1], True, True)
                app.authentication.authorization_code = params['code'][0]
                app.authentication.get_access_token()

    server_address = ('', 8000)
    httpd = BaseHTTPServer.HTTPServer(server_address, MyHandler)
    httpd.handle_request()
