class BaseLinkedInError(Exception):
    pass


class LinkedInHTTPError(BaseLinkedInError):
    pass


class LinkedInError(BaseLinkedInError):
    def __init__(self, error):
        if 'error' in error:
            Exception.__init__(self, u'%s: %s' % (error['error'],
                                                  error['error_description']))
        else:
            Exception.__init__(self, u'%s: %s' % ('Request Error',
                                                  error['message']))
