# -*- coding: utf-8 -*-

#######################################################################################
# Python implementation of LinkedIn OAuth Authorization, Profile and Connection APIs. #
#                                                                                     #
# Author: Ozgur Vatansever                                                            #
# Email : ozgurvt@gmail.com                                                           #
# LinkedIn Account: http://www.linkedin.com/in/ozgurvt                                #
#######################################################################################

__version__ = "1.8.1"

"""
Provides a Pure Python LinkedIn API Interface.
"""
try:
    import sha
except DeprecationWarning, derr:
    import hashlib
    sha = hashlib.sha1

import urllib, time, random, httplib, hmac, binascii, cgi, string
from HTMLParser import HTMLParser

from model import *

class OAuthError(Exception):
    """
    General OAuth exception, nothing special.
    """
    def __init__(self, value):
        self.parameter = value
        
    def __str__(self):
        return repr(self.parameter)


class Stripper(HTMLParser):
    """
    Stripper class that strips HTML entity.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)
    
    def getAlteredData(self):
        return ''.join(self.fed)


class XMLBuilder(object):
    def __init__(self, rootTagName):
        self.document = minidom.Document()
        self.root = self.document.createElement(rootTagName)
        self.document.appendChild(self.root)

    def xml(self):
        return self.document.toxml()

    def __unicode__(self):
        return self.document.toprettyxml()

    def append_element_to_root(self, element):
        self.root.appendChild(element)

    def append_list_of_elements_to_element(self, element, elements):
        map(lambda x:element.appendChild(x),elements)
        return element

    def create_element(self, tag_name):
        return self.document.createElement(str(tag_name))

    def create_element_with_text_node(self, tag_name, text_node):
        text_node = self.document.createTextNode(str(text_node))
        element = self.document.createElement(str(tag_name))
        element.appendChild(text_node)
        return element

    def create_elements(self, **elements):
        return [self.create_element_with_text_node(tag_name, text_node) for tag_name, text_node in elements.items()]
        
    


class ConnectionError(Exception):
    pass

class LinkedIn(object):
    def __init__(self, api_key, api_secret, callback_url, gae = False):
        """
        LinkedIn Base class that simply implements LinkedIn OAuth Authorization and LinkedIn APIs such as Profile, Connection vs.

        @ LinkedIn OAuth Authorization
        ------------------------------
        In OAuth terminology, there are 2 tokens that we need in order to have permission to perform an API request.
        Those are request_token and access_token. Thus, this class basicly intends to wrap methods of OAuth spec. which
        are related of gettting request_token and access_token strings.

        @ Important Note:
        -----------------
        HMAC-SHA1 hashing algorithm will be used while encrypting a request body of an HTTP request. Other alternatives
        such as 'SHA-1' or 'PLAINTEXT' are ignored.

        @Reference for OAuth
        --------------------
        Please take a look at the link below if you have a basic knowledge of HTTP protocol
        - http://developer.linkedin.com/docs/DOC-1008

        
        Please create an application from the link below if you do not have an API key and secret key yet.
        - https://www.linkedin.com/secure/developer
        @api_key:    Your API key
        @api_secret: Your API secret key
        @callback_url: the return url when the user grants permission to Consumer.
        """
        # Credientials
        self.API_ENDPOINT      = "api.linkedin.com"
        self.BASE_URL          = "https://%s" % self.API_ENDPOINT
        self.VERSION           = "1.0"
        
        self._api_key       = api_key
        self._api_secret    = api_secret
        self._callback_url  = callback_url
        self._gae = gae # Is it google app engine
        self._request_token = None # that comes later
        self._access_token  = None # that comes later and later
        
        self._request_token_secret = None
        self._access_token_secret  = None
        
        self._verifier = None
        self._error    = None

    def request_token(self):
        """
        Performs the corresponding API which returns the request token in a query string
        The POST Querydict must include the following:
         * oauth_callback
         * oauth_consumer_key
         * oauth_nonce
         * oauth_signature_method
         * oauth_timestamp
         * oauth_version
        """
        self.clear()

        method = "GET"
        relative_url = "/uas/oauth/requestToken"
        
        query_dict = self._query_dict({"oauth_callback" : self._callback_url})
        
        self._calc_signature(self._get_url(relative_url), query_dict, self._request_token_secret, method)

        try:
            response = self._https_connection(method, relative_url, query_dict)
        except ConnectionError:
            return False
        
        oauth_problem = self._get_value_from_raw_qs("oauth_problem", response)
        if oauth_problem:
            self._error = oauth_problem
            return False

        self._request_token = self._get_value_from_raw_qs("oauth_token", response)
        self._request_token_secret = self._get_value_from_raw_qs("oauth_token_secret", response)
        return True

    def access_token(self, request_token = None, request_token_secret = None, verifier = None):
        """
        Performs the corresponding API which returns the access token in a query string
        Accroding to the link (http://developer.linkedin.com/docs/DOC-1008), POST Querydict must include the following:
        * oauth_consumer_key
        * oauth_nonce
        * oauth_signature_method
        * oauth_timestamp
        * oauth_token (request token)
        * oauth_version
        """
        self._request_token = request_token and request_token or self._request_token
        self._request_token_secret = request_token_secret and request_token_secret or self._request_token_secret
        self._verifier = verifier and verifier or self._verifier
        # if there is no request token, fail immediately
        if self._request_token is None:
            raise OAuthError("There is no Request Token. Please perform 'request_token' method and obtain that token first.")

        if self._request_token_secret is None:
            raise OAuthError("There is no Request Token Secret. Please perform 'request_token' method and obtain that token first.")

        if self._verifier is None:
            raise OAuthError("There is no Verifier Key. Please perform 'request_token' method, redirect user to API authorize page and get the _verifier.")
        
        method = "GET"
        relative_url = "/uas/oauth/accessToken"
        query_dict = self._query_dict({
                    "oauth_token" : self._request_token,
                    "oauth_verifier" : self._verifier
                    })

        self._calc_signature(self._get_url(relative_url), query_dict, self._request_token_secret, method)

        try:
            response = self._https_connection(method, relative_url, query_dict)
        except ConnectionError:
            return False

        oauth_problem = self._get_value_from_raw_qs("oauth_problem", response)
        if oauth_problem:
            self._error = oauth_problem
            return False

        self._access_token = self._get_value_from_raw_qs("oauth_token", response)
        self._access_token_secret = self._get_value_from_raw_qs("oauth_token_secret", response)
        return True

    def get_profile(self, member_id = None, url = None, fields=[]):
        """
        Gets the public profile for a specific user. It is determined by his/her member id or public url.
        If none of them is given, the information og the application's owner are returned.

        If none of them are given, current user's details are fetched.
        The argument 'fields' determines how much information will be fetched.

        Examples:
        client.get_profile(merber_id = 123, url = None, fields=['first-name', 'last-name']) : fetches the profile of a user whose id is 123. 

        client.get_profile(merber_id = None, url = None, fields=['first-name', 'last-name']) : fetches current user's profile

        client.get_profile(member_id = None, 'http://www.linkedin.com/in/ozgurv') : fetches the profile of a  user whose profile url is http://www.linkedin.com/in/ozgurv
        
        @ Returns Profile instance
        """
        #################
        # BEGIN ROUTINE #
        #################
        # if there is no access token or secret, fail immediately
        self._check_tokens()
        
        # specify the url according to the parameters given
        raw_url = "/v1/people/"
        if url:
            url = self._quote(url)
            raw_url = (raw_url + "url=%s:public") % url
        elif member_id:
            raw_url = (raw_url + "id=%s" % member_id)
        else:
            raw_url = raw_url + "~"
        if url is None:
            fields = ":(%s)" % ",".join(fields) if len(fields) > 0 else None
            if fields:
                raw_url = raw_url + fields
                
        try:
            response = self._do_normal_query(raw_url)
            return Profile.create(response) # this creates Profile instance or gives you null
        except ConnectionError:
            return None

    def get_connections(self, member_id = None, public_url = None, fields=[]):
        """
        Fetches the connections of a user whose id is the given member_id or url is the given public_url
        If none of the parameters given, the connections of the current user are fetched.
        @Returns: a list of Profile instances or an empty list if there is no connection.

        Example urls:
        * http://api.linkedin.com/v1/people/~/connections (for current user)
        * http://api.linkedin.com/v1/people/id=12345/connections (fetch with member_id)
        * http://api.linkedin.com/v1/people/url=http%3A%2F%2Fwww.linkedin.com%2Fin%2Flbeebe/connections (fetch with public_url)
        """
        self._check_tokens()
        
        raw_url = "/v1/people/%s/connections"
        if member_id:
            raw_url = raw_url % ("id=" + member_id)
        elif public_url:
            raw_url = raw_url % ("url=" + self._quote(public_url))
        else:
            raw_url = raw_url % "~"
        fields = ":(%s)" % ",".join(fields) if len(fields) > 0 else None
        if fields:
            raw_url = raw_url + fields

        try:
            response = self._do_normal_query(raw_url)
            document = minidom.parseString(response)
            connections = document.getElementsByTagName("person")
            result = []
            for connection in connections:
                profile = Profile.create(connection.toxml())
                if profile is not None:
                    result.append(profile)
    
            return result
        except ConnectionError:
            return None

    def get_search(self, parameters):
        """
        Use the Search API to find LinkedIn profiles using keywords,
        company, name, or other methods. This returns search results,
        which are an array of matching member profiles. Each matching
        profile is similar to a mini-profile popup view of LinkedIn
        member profiles.

        Request URL Structure:
        http://api.linkedin.com/v1/people?keywords=['+' delimited keywords]&name=[first name + last name]&company=[company name]&current-company=[true|false]&title=[title]&current-title=[true|false]&industry-code=[industry code]&search-location-type=[I,Y]&country-code=[country code]&postal-code=[postal code]&network=[in|out]&start=[number]&count=[1-10]&sort-criteria=[ctx|endorsers|distance|relevance]
        """
        self._check_tokens()

        try:
            response = self._do_normal_query("/v1/people", method="GET", params=parameters)
        except ConnectionError:
            return None
        
        error = self._parse_error(response)
        if error:
            self._error = error
            return None
        
        document = minidom.parseString(response)
        connections = document.getElementsByTagName("person")
        result = []
        for connection in connections:
            profile = Profile.create(connection.toxml())
            if profile is not None:
                result.append(profile)
        return result

    def send_message(self, subject, message, ids = [], send_yourself = False):
        """
        Sends a Non-HTML message and subject to the members whose IDs are given as a parameter 'ids'.
        If the user gives more than 10 ids, the IDs after 10th ID are ignored.
        @Input: string x string x list x bool
        @Output: bool
        Returns True if successfully sends the message otherwise returns False.

        Important Note: You can send a message at most 10 connections at one time.
        
        Technical Explanation:
        ---------------------
        Sends a POST request to the URL 'http://api.linkedin.com/v1/people/~/mailbox'.
        The XML that will be sent looks like this:
        <?xml VERSION='1.0' encoding='UTF-8'?>
          <mailbox-item>
            <recipients>
             <recipient>
               <person path='/people/{id}' />
             </recipient>
            </recipients>
            <subject>{subject}</subject>
            <body>{message}</body>
          </mailbox-item>

        The resulting XML would be like this:
        if result is None or '', it is guaranteed that you sent the message. If there occurs an error, you get the following:
        <?xml VERSION='1.0' encoding='UTF-8' standalone='yes'?>
         <error>
           <status>...</status>
           <timestamp>...</timestamp>
           <error-code>...</error-code>
           <message>...</message>
          </error>
        """
        #######################################################################################
        # What we do here is first we need to shorten to ID list to 10 elements just in case. #
        # Then we need to strip HTML tags using HTMLParser library.                           #
        # Then we are going  to build up the XML body and post the request.                   #
        # According to the response parsed, we return True or False.                          #
        #######################################################################################

        self._check_tokens()

        # Shorten the list.
        ids = ids[:10]
        if send_yourself:
            ids = ids[:9]
            ids.append("~")
            
        subjectStripper = Stripper()
        subjectStripper.feed(subject)
        subject = subjectStripper.getAlteredData()
        bodyStripper = Stripper()
        bodyStripper.feed(message)
        body = bodyStripper.getAlteredData()

        # Build up the POST body.
        builder = XMLBuilder("mailbox-item")
        recipients_element = builder.create_element("recipients")
        subject_element = builder.create_element_with_text_node("subject", subject)
        body_element = builder.create_element_with_text_node("body", body)
        for member_id in ids:
            recipient_element = builder.create_element("recipient")
            person_element = builder.create_element("person")
            person_element.setAttribute("path", "/people/%s" % member_id)
            recipient_element.appendChild(person_element)
            recipients_element.appendChild(recipient_element)

        builder.append_element_to_root(recipients_element)
        builder.append_element_to_root(subject_element)
        builder.append_element_to_root(body_element)
        body = builder.xml()
        
        try:
            response = self._do_normal_query("/v1/people/~/mailbox", body=body, method="POST")
            # If API server sends us a response, we know that there occurs an error.
            # So we have to parse the response to make sure what causes the error.
            # and let the user know by returning False.
            if response:
                self._error = self._parse_error(response)
                return False
        except ConnectionError:
            return False

        return True

    def send_invitation(self, subject, message, first_name, last_name, email):
        """
        Sends an invitation to the given email address.
        This method is very similiar to 'send_message' method.
        @input: string x string x string x string x string
        @output: bool
        """
        
        #########################################################################################
        # What we do here is first, we need to check the access token.                          #
        # Then we need to strip HTML tags using the HTMLParser library.                         #
        # Then we are going to build up the XML body and post the request.                      #
        # According to the response parsed, we return True or False.                            #
        #########################################################################################
        
        self._check_tokens()
        
        subjectStripper = Stripper()
        subjectStripper.feed(subject)
        subject = subjectStripper.getAlteredData()
        bodyStripper = Stripper()
        bodyStripper.feed(message)
        body = bodyStripper.getAlteredData()

        # Build up the POST body.
        builder = XMLBuilder("mailbox-item")
        recipients_element = builder.create_element("recipients")
        subject_element = builder.create_element_with_text_node("subject", subject)
        body_element = builder.create_element_with_text_node("body", body)
        recipient_element = builder.create_element("recipient")
        person_element = builder.create_element("person")
        person_element.setAttribute("path", "/people/email=%s" % email)
        first_name_element = builder.create_element_with_text_node("first-name", first_name)
        last_name_element = builder.create_element_with_text_node("last-name", last_name)
        builder.append_list_of_elements_to_element(person_element, [first_name_element, last_name_element])
        recipient_element.appendChild(person_element)
        recipients_element.appendChild(recipient_element)

        item_content_element = builder.create_element("item-content")
        invitation_request_element = builder.create_element("invitation-request")
        connect_type_element = builder.create_element_with_text_node("connect-type", "friend")
        invitation_request_element.appendChild(connect_type_element)
        item_content_element.appendChild(invitation_request_element)
        
        
        builder.append_element_to_root(recipients_element)
        builder.append_element_to_root(subject_element)
        builder.append_element_to_root(body_element)
        builder.append_element_to_root(item_content_element)
        body = builder.xml()

        try:
            response = self._do_normal_query("/v1/people/~/mailbox", body=body, method="POST")
            # If API server sends us a response, we know that there occurs an error.
            # So we have to parse the response to make sure what causes the error.
            # and let the user know by returning False.
            if response:
                self._error = self._parse_error(response)
                return False
        except ConnectionError:
            return False

        return True

    def set_status(self, status_message):
        """
        This API is deprecated and should be replaced with the share status of linkedin 
        
        Issues a status of the connected user. There is a 140 character limit on status message.
        If it is longer than 140 characters, it is shortened.
        -----------
        Usage Rules
        * We must use an access token from the user.
        * We can only set status for the user who grants us access.
        -----------
        @input: string
        @output: bool
        """
        self._check_tokens()

        # Shorten the message just in case.
        status_message = str(status_message)
        if len(status_message) > 140:
            status_message = status_message[:140]

        # Build up the XML request
        builder = XMLBuilder("current-status")
        status_node = builder.document.createTextNode(status_message)
        builder.root.appendChild(status_node)
        body = builder.xml()
        
        try:
            response = self._do_normal_query("/v1/people/~/current-status", body=body, method="PUT")
            # If API server sends us a response, we know that there occurs an error.
            # So we have to parse the response to make sure what causes the error.
            # and let the user know by returning False.
            if response:
                self._error = self._parse_error(response)
                return False
        except ConnectionError:
            return False

        return True
        
    def clear_status(self):
        """
        This API is deprecated and should be replaced with the share status of linkedin
        
        Clears the status of the connected user.
        -----------
        Usage Rules
        * We must use an access token from the user.
        * We can only set status for the user who grants us access.
        -----------
        @input: none
        @output: bool
        """
        self._check_tokens()

        try:
            response = self._do_normal_query("/v1/people/~/current-status", method="DELETE")
            # If API server sends us a response, we know that there occurs an error.
            # So we have to parse the response to make sure what causes the error.
            # and let the user know by returning False.
            if response:
                self._error = self._parse_error(response)
                return False
        except ConnectionError:
            return False

        return True
    
    def share_update(self, comment=None, title=None, submitted_url=None,
                    submitted_image_url=None, description=None,
                    visibility="connections-only"):
        """
        Use the Share API to have a member share content with their network or with all of LinkedIn
        -----------
        Usage Rules
        * We must use an access token from the user.
        * We can only share items for the user who grants us access.
        -----------
        visibility: anyone or connections-only

        @output: bool

        SAMPLE 
            <?xml VERSION="1.0" encoding="UTF-8"?>
            <share>
              <comment>83% of employers will use social media to hire: 78% LinkedIn, 55% Facebook, 45% Twitter [SF Biz Times] http://bit.ly/cCpeOD</comment>
              <content>
                 <title>Survey: Social networks top hiring tool - San Francisco Business Times</title>
                 <submitted-url>http://sanfrancisco.bizjournals.com/sanfrancisco/stories/2010/06/28/daily34.html</submitted-url>
                 <submitted-image-url>http://images.bizjournals.com/travel/cityscapes/thumbs/sm_sanfrancisco.jpg</submitted-image-url>
              </content>
              <visibility>
                 <code>anyone</code>
              </visibility>
            </share>


        """
        self._check_tokens()

        if comment is not None:
            comment = str(comment)
            if len(comment) > 700:
                comment = comment[:700]

        if title is not None:
            title = str(title)
            if len(title) > 200:
                title = title[:200]

        if description is not None:
            description = str(description)
            if len(description) > 400:
                description = description[:400]

        # Build up the XML request
        builder = XMLBuilder("share")

        if len(comment) > 0:
            comment_element = builder.create_element_with_text_node("comment", comment)
            builder.append_element_to_root(comment_element)


        if (submitted_url is not None) or (title is not None):
            content_element = builder.create_element("content")
            if submitted_url is not None:
                submitted_url_element = builder.create_element_with_text_node("submitted-url", submitted_url)
                content_element.appendChild(submitted_url_element)

                # must have url to inlcude image url
                if submitted_image_url is not None:
                    submitted_image_url_element = builder.create_element_with_text_node("submitted-image-url", submitted_image_url)
                    content_element.appendChild(submitted_image_url_element)

            if title is not None:
                title_element = builder.create_element_with_text_node("title", title)
                content_element.appendChild(title_element)

            if description is not None:
                description_element = builder.create_element_with_text_node("description", description)
                content_element.appendChild(description_element)

            builder.append_element_to_root(content_element)

        visibility_element = builder.create_element("visibility")
        code_element = builder.create_element_with_text_node("code", visibility)
        visibility_element.appendChild(code_element)


        builder.append_element_to_root(visibility_element)

        body = builder.xml()        

        try:
            response = self._do_normal_query("/v1/people/~/shares", body=body, method="POST")
            # If API server sends us a response, we know that there occurs an error.
            # So we have to parse the response to make sure what causes the error.
            # and let the user know by returning False.
            if response:
                self._error = self._parse_error(response)
                return False
        except ConnectionError:
            return False

        return True

    def get_authorize_url(self, request_token = None):
        self._request_token = request_token and request_token or self._request_token
        if self._request_token is None:
            raise OAuthError("OAuth Request Token is NULL. Plase acquire this first.")
        return "%s%s?oauth_token=%s" % (self.BASE_URL, "/uas/oauth/authorize", self._request_token)

    def get_error(self):
        return self._error
    
    def clear(self):
        self._request_token = None
        self._access_token  = None
        self._verifier      = None

        self._request_token_secret = None
        self._access_token_secret = None
        
        self._error                   = None
        
    #################################################
    # HELPER FUNCTIONS                              #
    # You do not explicitly use those methods below #
    #################################################
    
    def _generate_nonce(self, length = 20):
        return ''.join([string.letters[random.randint(0, len(string.letters) - 1)] for i in range(length)])

    def _get_url(self, relative_path):
        return self.BASE_URL + relative_path
    
    def _generate_timestamp(self):
        return str(int(time.time()))
    
    def _quote(self, st):
        return urllib.quote(st, safe='~')

    def _utf8(self, st):
        return isinstance(st, unicode) and st.encode("utf-8") or str(st)

    def _urlencode(self, query_dict):
        keys_and_values = [(self._quote(self._utf8(k)), self._quote(self._utf8(v))) for k,v in query_dict.items()]
        keys_and_values.sort()
        return '&'.join(['%s=%s' % (k, v) for k, v in keys_and_values])

    def _get_value_from_raw_qs(self, key, qs):
        raw_qs = cgi.parse_qs(qs, keep_blank_values = False)
        rs = raw_qs.get(key)
        if type(rs) == list:
            return rs[0]
        else:
            return rs

    def _signature_base_string(self, method, uri, query_dict):
        return "&".join([self._quote(method), self._quote(uri), self._quote(self._urlencode(query_dict))])
        
    def _parse_error(self, str_as_xml):
        """
        Helper function in order to get error message from an xml string.
        In coming xml can be like this:
        <?xml VERSION='1.0' encoding='UTF-8' standalone='yes'?>
        <error>
         <status>404</status>
         <timestamp>1262186271064</timestamp>
         <error-code>0000</error-code>
         <message>[invalid.property.name]. Couldn't find property with name: first_name</message>
        </_error>
        """
        try:
            xmlDocument = minidom.parseString(str_as_xml)
            if len(xmlDocument.getElementsByTagName("error")) > 0: 
                error = xmlDocument.getElementsByTagName("message")
                if error:
                    error = error[0]
                    return error.childNodes[0].nodeValue
            return None
        except OAuthError, detail:
#            raise detail
            raise OAuthError("Invalid XML String given: error: %s" % repr(detail))
        
    def _create_oauth_header(self, query_dict):
        header = 'OAuth realm="http://api.linkedin.com", '
        header += ", ".join(['%s="%s"' % (k, self._quote(query_dict[k]))
                           for k in sorted(query_dict)])
        return header
    
    def _query_dict(self, additional = {}):
        query_dict = {"oauth_consumer_key": self._api_key,
                      "oauth_nonce": self._generate_nonce(),
                      "oauth_signature_method": "HMAC-SHA1",
                      "oauth_timestamp": self._generate_timestamp(),
                      "oauth_version": self.VERSION
        }
        query_dict.update(additional)
        return query_dict
    
    def _do_normal_query(self, relative_url, body=None, method="GET", params=None):
        method = method
        query_dict = self._query_dict({"oauth_token" : self._access_token})
        signature_dict = dict(query_dict)
        
        if (params):
            signature_dict.update(params)
            
        query_dict["oauth_signature"] = self._calc_signature(self._get_url(relative_url),
                                    signature_dict, self._access_token_secret, method, update=False)
        
        if (params):
            relative_url = "%s?%s" % (relative_url, self._urlencode(params))
        
        response = self._https_connection(method, relative_url, query_dict, body)
        
        if (response):
            error = self._parse_error(response)
            if error:
                self._error = error
                raise ConnectionError()
        
        return response

    def _check_tokens(self):
        if self._access_token is None:
            self._error = "There is no Access Token. Please perform 'access_token' method and obtain that token first."
            raise OAuthError(self._error)
        if self._access_token_secret is None:
            self._error = "There is no Access Token Secret. Please perform 'access_token' method and obtain that token first."
            raise OAuthError(self._error)

    def _calc_key(self, token_secret):
        key = self._quote(self._api_secret) + "&"
        if (token_secret):
            key += self._quote(token_secret)
        return key

    def _calc_signature(self, url, query_dict, token_secret, method = "GET", update=True):
        query_string = self._quote(self._urlencode(query_dict))
        signature_base_string = "&".join([self._quote(method), self._quote(url), query_string])
        hashed = hmac.new(self._calc_key(token_secret), signature_base_string, sha)
        signature = binascii.b2a_base64(hashed.digest())[:-1]
        if (update):
            query_dict["oauth_signature"] = signature
        return signature
        
    def _https_connection(self, method, relative_url, query_dict, body=None):
        if (self._gae):
            return self._https_connection_gae(method, relative_url, query_dict, body)
        else:
            return self._https_connection_regular(method, relative_url, query_dict, body)
    
    def _https_connection_regular(self, method, relative_url, query_dict, body = None):
        header = self._create_oauth_header(query_dict)
        connection = None
        try:
            connection = httplib.HTTPSConnection(self.API_ENDPOINT)
            connection.request(method, relative_url, body = body,
                               headers={'Authorization':header})
            response = connection.getresponse()
            
            if response is None:
                self._error = "No HTTP response received."
                raise ConnectionError()
            return response.read()
        finally:
            if (connection):
                connection.close()
    
    def _https_connection_gae(self, method, relative_url, query_dict, body = None):
        from google.appengine.api import urlfetch
        if (method == "GET"):
            method = urlfetch.GET
        elif (method == "POST"):
            method = urlfetch.POST
        elif (method == "PUT"):
            method = urlfetch.PUT
        elif (method == "DELETE"):
            method = urlfetch.DELETE
        
        header = self._create_oauth_header(query_dict)
        headers = {'Authorization':header}
        if (body):
            headers["Content-Type"] = "text/xml"
        
        url = self._get_url(relative_url)

        rpc = urlfetch.create_rpc(deadline=10.0)
        urlfetch.make_fetch_call(rpc, url, method=method, headers=headers,
                             payload=body)
        
        return rpc.get_result().content
    
    ########################
    # END HELPER FUNCTIONS #
    ########################
