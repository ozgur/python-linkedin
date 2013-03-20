# -*- coding: utf-8 -*-

import requests
import urllib
import random
import hashlib
import collections
import contextlib
import json

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import urllib, time, random, httplib, hmac, binascii, cgi, string
from HTMLParser import HTMLParser

from .model import *
from .utils import make_enum, to_utf8, HTTP_METHODS

PERMISSIONS = make_enum('Permission',
                        BASIC_PROFILE='r_basicprofile',
                        FULL_PROFILE='r_fullprofile',
                        EMAIL_ADDRESS='r_emailaddress',
                        NETWORK='r_network',
                        CONTACT_INFO='r_contactinfo',
                        NETWORK_UPDATES='rw_nus',
                        GROUPS='rw_groups',
                        MESSAGES='w_messages')


ENDPOINTS = make_enum('LinkedInURL',
                      PEOPLE='https://api.linkedin.com/v1/people',
                      PEOPLE_SEARCH='https://api.linkedin.com/v1/people-search',
                      GROUPS='https://api.linkedin.com/v1/groups',
                      POSTS='https://api.linkedin.com/v1/posts',
                      COMPANIES='https://api.linkedin.com/v1/companies',
                      COMPANY_SEARCH='https://api.linkedin.com/v1/company-search',
                      JOBS='https://api.linkedin.com/v1/jobs',
                      JOB_SEARCH='https://api.linkedin.com/v1/job-search')


AccessToken = collections.namedtuple('AccessToken', ['access_token', 'expires_in'],
                                     verbose=False, rename=False)


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


class LinkedInAuthentication(object):
    def __init__(self, key, secret, redirect_uri, permissions=[]):
        self.AUTHORIZATON_URL = 'https://www.linkedin.com/uas/oauth2/authorization'
        self.ACCESS_TOKEN_URL = 'https://www.linkedin.com/uas/oauth2/accessToken'
        self.key = key
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.permissions = permissions
        self.state = None
        self.authorization_code = None
        self.token = None

    @property
    def authorization_url(self):
        self.state = self.get_new_state()
        qd = {'response_type': 'code',
              'client_id': self.key,
              'scope': (' '.join(self.permissions)).strip(),
              'state': self.state,
              'redirect_uri': self.redirect_uri}
        # urlencode uses quote_plus when encoding the query string so,
        # we ought to be encoding the qs by on our own.
        qsl = ['%s=%s' % (urllib.quote(k), urllib.quote(v)) for k, v in qd.items()]
        return '%s?%s' % (self.AUTHORIZATON_URL, '&'.join(qsl))

    def get_new_state(self):
        return hashlib.md5(
            '%s%s' % (random.randrange(0, 2**63), self.secret)).hexdigest()

    def get_access_token(self, timeout=60):
        assert self.authorization_code, 'You must first get the AUTHORIZATION CODE'
        qd = {'grant_type': 'authorization_code',
              'code': self.authorization_code,
              'redirect_uri': self.redirect_uri,
              'client_id': self.key,
              'client_secret': self.secret}
        try:
            response = requests.post(self.ACCESS_TOKEN_URL, data=qd, timeout=timeout)
            response.raise_for_status()
            response = response.json()
        except (requests.HTTPError, requests.ConnectionError), error:
            raise LinkedInHTTPError(error.message)
        else:
            if 'error' in response:
                raise LinkedInError(response)
        self.token = AccessToken(response['access_token'], response['expires_in'])
        return self.token


class LinkedInSelector(object):
    @classmethod
    def parse(cls, selector):
        with contextlib.closing(StringIO()) as result:
            if type(selector) == dict:
                for k, v in selector.items():
                    result.write('%s:(%s)' % (to_utf8(k), cls.parse(v)))
            elif type(selector) in (list, tuple):
                result.write(','.join(map(cls.parse, selector)))
            else:
                result.write(to_utf8(selector))
            return result.getvalue()


class LinkedInApplication(object):
    def __init__(self, authentication):
        assert authentication, 'Authentication instance must be provided'
        assert type(authentication) == LinkedInAuthentication, 'Auth type mismatch'
        self.BASE_URL = 'https://api.linkedin.com'
        self.authentication = authentication

    def request_succeeded(self, response):
        return not (('error' in response) or ('errorCode' in response))

    def make_request(self, method, url, data=None, params=None, headers=None,
                     timeout=60):
        if headers is None:
            headers = {'x-li-format': 'json', 'Content-Type': 'application/json'}
        else:
            headers.update({'x-li-format': 'json', 'Content-Type': 'application/json'})

        if params is None:
            params = {'oauth2_access_token': self.authentication.token.access_token}
        else:
            params['oauth2_access_token'] = self.authentication.token.access_token

        print locals()
        print method, '=>', url, repr(headers)
        return requests.request(method.upper(), url, data=data, params=params,
                                headers=headers, timeout=timeout)

    def get_profile(self, member_id=None, member_url=None, selectors=None,
                    params=None, headers=None):
        if member_id:
            url = '%s/id=%s' % (ENDPOINTS.PEOPLE, str(member_id))
        elif member_url:
            url = '%s/url=%s' % (ENDPOINTS.PEOPLE, urllib.quote_plus(member_url))
        else:
            url = '%s/~' % ENDPOINTS.PEOPLE
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if 'error' in response:
                raise LinkedInError(response)
            return response

    def search_profile(self, selectors=None, params=None, headers=None):
        if selectors:
            url = '%s:(%s)' % (ENDPOINTS.PEOPLE_SEARCH,
                               LinkedInSelector.parse(selectors))
        else:
            url = ENDPOINTS.PEOPLE_SEARCH
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if 'error' in response:
                raise LinkedInError(response)
            return response

    def get_connections(self, member_id=None, member_url=None, selectors=None,
                        params=None, headers=None):
        if member_id:
            url = '%s/id=%s/connections' % (ENDPOINTS.PEOPLE, str(member_id))
        elif member_url:
            url = '%s/url=%s/connections' % (ENDPOINTS.PEOPLE,
                                             urllib.quote_plus(member_url))
        else:
            url = '%s/~/connections' % ENDPOINTS.PEOPLE
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_memberships(self, member_id=None, member_url=None, group_id=None,
                        selectors=None, params=None, headers=None):
        if member_id:
            url = '%s/id=%s/group-memberships' % (ENDPOINTS.PEOPLE, str(member_id))
        elif member_url:
            url = '%s/url=%s/group-memberships' % (ENDPOINTS.PEOPLE,
                                                   urllib.quote_plus(member_url))
        else:
            url = '%s/~/group-memberships' % ENDPOINTS.PEOPLE

        if group_id:
            url = '%s/%s' % (url, str(group_id))

        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_group(self, group_id, selectors=None, params=None, headers=None):
        url = '%s/%s' % (ENDPOINTS.GROUPS, str(group_id))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_posts(self, group_id, post_ids=None, selectors=None, params=None,
                  headers=None):
        url = '%s/%s/posts' % (ENDPOINTS.GROUPS, str(group_id))
        if post_ids:
            url = '%s::(%s)' % (url, ','.join(map(str, post_ids)))
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def join_group(self, group_id):
        url = '%s/~/group-memberships/%s' % (ENDPOINTS.PEOPLE, str(group_id))
        try:
            response = self.make_request('PUT', url,
                    data=json.dumps({'membershipState': {'code': 'member'}}))
            response.raise_for_status()
        except (requests.ConnectionError, HTTPError), error:
            raise LinkedInHTTPError(error.message)
        else:
            return True

    def leave_group(self, group_id):
        url = '%s/~/group-memberships/%s' % (ENDPOINTS.PEOPLE, str(group_id))
        try:
            response = self.make_request('DELETE', url)
            response.raise_for_status()
        except (requests.ConnectionError, HTTPError), error:
            raise LinkedInHTTPError(error.message)
        else:
            return True

    def submit_group_post(self, group_id, title, summary, submitted_url,
                          submitted_image_url, content_title, description):
        post = {
            'title': title, 'summary': summary,
            'content': {
                'submitted-url': submitted_url,
                'submitted-image-url': submitted_image_url,
                'title': content_title,
                'description': description
            }
        }
        url = '%s/%s/posts' % (ENDPOINTS.GROUPS, str(group_id))
        try:
            response = self.make_request('POST', url, data=json.dumps(post))
            response = response.json()
        except (requests.ConnectionError, HTTPError), error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return True

    def get_companies(self, company_ids=None, universal_names=None, selectors=None,
                      params=None, headers=None):
        identifiers = []
        url = ENDPOINTS.COMPANIES
        if company_ids:
            identifiers += map(str, company_ids)

        if universal_names:
            identifiers += ['universal-name=%s' % un for un in universal_names]

        if identifiers:
            url = '%s::(%s)' % (url, ','.join(identifiers))

        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))

        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_company_updates(self, company_id, params=None, headers=None):
        url = '%s/%s/updates' % (ENDPOINTS.COMPANIES, str(company_id))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_company_products(self, company_id, selectors=None, params=None,
                             headers=None):
        url = '%s/%s/products' % (ENDPOINTS.COMPANIES, str(company_id))
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def follow_company(self, company_id):
        url = '%s/~/following/companies' % ENDPOINTS.PEOPLE
        post = {'id': company_id}
        try:
            response = self.make_request('POST', url, data=json.dumps(post))
            response = response.json()
        except (requests.ConnectionError, HTTPError), error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return True

    def unfollow_company(self, company_id):
        url = '%s/~/following/companies/id=%s' % (ENDPOINTS.PEOPLE, str(company_id))
        try:
            response = self.make_request('DELETE', url)
            response.raise_for_status()
        except (requests.ConnectionError, HTTPError), error:
            raise LinkedInHTTPError(error.message)
        else:
            return True

    def search_company(self, selectors=None, params=None, headers=None):
        url = ENDPOINTS.COMPANY_SEARCH
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_job(self, job_id, selectors=None, params=None, headers=None):
        url = '%s/%s' % (ENDPOINTS.JOBS, str(job_id))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def get_job_bookmarks(self, selectors=None, params=None, headers=None):
        url = '%s/~/job-bookmarks' % ENDPOINTS.PEOPLE
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response

    def search_job(self, selectors=None, params=None, headers=None):
        url = ENDPOINTS.JOB_SEARCH
        if selectors:
            url = '%s:(%s)' % (url, LinkedInSelector.parse(selectors))
        try:
            response = self.make_request('GET', url, params=params, headers=headers)
            response = response.json()
        except requests.ConnectionError as error:
            raise LinkedInHTTPError(error.message)
        else:
            if not self.request_succeeded(response):
                raise LinkedInError(response)
            return response




if __name__ == '__main__':
    authentication = LinkedInAuthentication('wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl', 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG', 'http://localhost', PERMISSIONS.enums.values())
    authentication.token = AccessToken(access_token=u'AQXbxD10Rxxp17Yiru-9MNf3Glb6jxwQJmwkO_ip9x6G-8XA9eiccC0C_re3icyDSUTrU27ckoeusvFmLWdCVL7_Xa32ccdJkj-RiKsWiPWeNRswD5xkuhuGasJKfjnrMFGtUZlG9MVOATT5B-Eg5XFuuoFLMcgVvo-LAe0jgE5Rbj2FqZ0', expires_in=5182360)

    application = LinkedInApplication(authentication)
