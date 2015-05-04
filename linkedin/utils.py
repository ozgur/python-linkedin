# -*- coding: utf-8 -*-
import requests
from .exceptions import LinkedInError, get_exception_for_error_code
import sys
from io import StringIO

try:
    import simplejson as json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import json


if sys.version_info < (3,):
    import __builtin__

    def to_utf8(x):
        return __builtin__.unicode(x)

    def to_string(x):
        return str(x)
else:
    def to_utf8(x):
        return x

    def to_string(x):
        return x


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
    for k, v in methods.items():
        methods[k] = classmethod(v)

    attrs['enums'] = attrs.copy()
    methods.update(attrs)
    methods['__init__'] = __init__
    return type(to_string(enum_type), base_classes, methods)

def raise_for_error(response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as error:
        try:
            if len(response.content) == 0:
                # There is nothing we can do here since LinkedIn has neither sent
                # us a 2xx response nor a response content.
                return
            response = response.json()
            if ('error' in response) or ('errorCode' in response):
                message = '%s: %s' % (response.get('error', str(error)),
                                      response.get('message', 'Unknown Error'))
                error_code = response.get('status')
                ex = get_exception_for_error_code(error_code)
                raise ex(message)
            else:
                raise LinkedInError(error.message)
        except (ValueError, TypeError):
            raise LinkedInError(error.message)


HTTP_METHODS = enum('HTTPMethod', GET='GET', POST='POST',
                    PUT='PUT', DELETE='DELETE', PATCH='PATCH')
