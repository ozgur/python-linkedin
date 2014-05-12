# -*- coding: utf-8 -*-
import requests
from .exceptions import LinkedInError

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import simplejson as json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import json


def enum(enum_type='enum', base_classes=None, methods=None, **attrs):
    """
    Generates a enumeration with the given attributes.
    """
    # Enumerations can not be initalized as a new instance
    def __init__(instance, *args, **kwargs):
        raise RuntimeError('%s types can not be initialized.' % enum_type)

    if base_classes is None:
        base_classes = ()

    if methods is None:
        methods = {}

    base_classes = base_classes + (object,)
    for k, v in methods.iteritems():
        methods[k] = classmethod(v)

    attrs['enums'] = attrs.copy()
    methods.update(attrs)
    methods['__init__'] = __init__
    return type(enum_type, base_classes, methods)


def to_utf8(st):
    if isinstance(st, unicode):
        return st.encode('utf-8')
    else:
        return bytes(st)


def raise_for_error(response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError), error:
        try:
            if len(response.content) == 0:
                # There is nothing we can do here since LinkedIn has neither sent
                # us a 2xx response nor a response content.
                return
            response = response.json()
            if ('error' in response) or ('errorCode' in response):
                message = '%s: %s' % (response.get('error', error.message),
                                      response.get('error_description', 'Unknown Error'))
                raise LinkedInError(message)
            else:
                raise LinkedInError(error.message)
        except (ValueError, TypeError):
            raise LinkedInError(error.message)

HTTP_METHODS = enum('HTTPMethod', GET='GET', POST='POST',
                    PUT='PUT', DELETE='DELETE', PATCH='PATCH')
