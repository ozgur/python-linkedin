import linkedin

def quick_api(api_key, secret_key):
    """ This method helps you get access to linkedin api quickly when using it
    from the interpreter.
    Notice that this method creates http server and wait for a request, so it
    shouldn't be used in real production code - it's just an helper for debugging

    The usage is basically:
    api = quick_api(KEY, SECRET)
    After you do that, it will print a URL to the screen which you must go in
    and allow the access, after you do that, the method will return with the api object.
    """
    
    api = linkedin.LinkedIn(api_key, secret_key, "http://localhost:8000/")
    api.request_token()
    print "Put this url in your browser and allow the permissions:"
    print api.get_authorize_url()
    _wait_for_user_to_enter_browser(api)
    api.access_token()
    return api
    
def _wait_for_user_to_enter_browser(api):
        import BaseHTTPServer
        class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
            def do_GET(self):
                p = self.path.split("?")
                params = {}
                if len(p) > 1:
                    import cgi
                    params = cgi.parse_qs(p[1], True, True)
                    api._verifier = params["oauth_verifier"][0]

        server_address = ('', 8000)
        httpd = BaseHTTPServer.HTTPServer(server_address, MyHandler)
        httpd.handle_request()