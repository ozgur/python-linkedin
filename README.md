# Python LinkedIn

Python interface to the LinkedIn API

[![LinkedIn](http://developer.linkedin.com/sites/default/files/LinkedIn_Logo60px.png)](http://developer.linkedin.com)

This library provides a pure Python interface to the LinkedIn  **Profile**, **Group**, **Company**, **Jobs**, **Search**, **Share**, **Network** and **Invitation** REST APIs.

[LinkedIn](http://developer.linkedin.com) provides a service that lets people bring their LinkedIn profiles and networks with them to your site or application via their OAuth based API. This library provides a lightweight interface over a complicated LinkedIn OAuth based API to make it for python programmers easy to use.

## Installation

[![Build Status](https://travis-ci.org/ozgur/python-linkedin.png?branch=master)](https://travis-ci.org/ozgur/python-linkedin)

You can install **python-linkedin** library via pip:

    $ pip install python-linkedin

## Authentication

LinkedIn REST API uses **Oauth 2.0** protocol for authentication. In order to use the LinkedIn API, you have an **application key** and **application secret**. You can get more detail from [here](http://developers.linkedin.com/documents/authentication).

For debugging purposes you can use the credentials below. It belongs to my test application. Nothing's harmful.

```python
KEY = 'wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl'
SECRET = 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG'
```
You can also get those keys from [here](http://developer.linkedin.com/rest).

LinkedIn redirects the user back to your website's URL after granting access (giving proper permissions) to your application. We call that url **RETURN URL**. Assuming your return url is **http://localhost:8000**, you can write something like this:

```python
from linkedin import linkedin

API_KEY = 'wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl'
API_SECRET = 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG'
RETURN_URL = 'http://localhost:8000'

authentication = linkedin.LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL, linkedin.PERMISSIONS.enums.values())
print authentication.authorization_url  # open this url on your browser
application = linkedin.LinkedInApplication(authentication)
```
When you grant access to the application, you will be redirected to the return url with the following query strings appended to your **RETURN_URL**:

```python
"http://localhost:8000/?code=AQTXrv3Pe1iWS0EQvLg0NJA8ju_XuiadXACqHennhWih7iRyDSzAm5jaf3R7I8&state=ea34a04b91c72863c82878d2b8f1836c"
```

This means that the value of the **authorization_code** is **AQTXrv3Pe1iWS0EQvLg0NJA8ju_XuiadXACqHennhWih7iRyDSzAm5jaf3R7I8**. After setting it by hand, we can call the **.get_access_token()** to get the actual token.

```python
authentication.authorization_code = 'AQTXrv3Pe1iWS0EQvLg0NJA8ju_XuiadXACqHennhWih7iRyDSzAm5jaf3R7I8'
authentication.get_access_token()
```

## Quick Usage From Python Interpreter

For testing the library using an interpreter, you can benefit from the test server.

```python
from linkedin import server
application = server.quick_api(KEY, SECRET)
```
This will print a url to the screen. Go into this URL using a browser to grant access to the test application. After you do so, the method will return with an API object you can now use.

## Profile API
The Profile API returns a member's LinkedIn profile. You can use this call to return one of two versions of a user's profile which are **public profile** and **standart profile**. For more information, check out the [documentation](http://developers.linkedin.com/documents/profile-api).

```python
application.get_profile()
{u'firstName': u'ozgur',
 u'headline': u'This is my headline',
 u'lastName': u'vatansever',
 u'siteStandardProfileRequest': {u'url': u'http://www.linkedin.com/profile/view?id=46113651&authType=name&authToken=Egbj&trk=api*a101945*s101945*'}}
```

There are many **field selectors** that enable the client fetch more information from the API. All of them used by each API are listed [here](http://developers.linkedin.com/documents/field-selectors).

```python
application.get_profile(selectors=['id', 'first-name', 'last-name', 'location', 'distance', 'num-connections', 'skills', 'educations'])
{u'distance': 0,
 u'educations': {u'_total': 1,
  u'values': [{u'activities': u'This is my activity and society field',
    u'degree': u'graduate',
    u'endDate': {u'year': 2009},
    u'fieldOfStudy': u'computer science',
    u'id': 42611838,
    u'notes': u'This is my additional notes field',
    u'schoolName': u'\u0130stanbul Bilgi \xdcniversitesi',
    u'startDate': {u'year': 2004}}]},
 u'firstName': u'ozgur',
 u'id': u'COjFALsKDP',
 u'lastName': u'vatansever',
 u'location': {u'country': {u'code': u'tr'}, u'name': u'Istanbul, Turkey'},
 u'numConnections': 13}
```



To fetch your connections, simply call:

```python
connections = api.get_connections()
```

You can set/clear your status by calling **.set_status()** or **.clear_status()** methods. If you get False as the result, you can get the error by calling **.get_error()** method. Status message should be less than 140 characters. If it is too long, it is shortened. For more information, you can take a look at [http://developer.linkedin.com/docs/DOC-1007](http://developer.linkedin.com/docs/DOC-1007)

```python
result = api.set_status('This is my status.')
result = api.clear_status()
```

You can send a message to yourself or your connections' inboxes by simply calling **.send_message()** method. You can send your message at most 10 connections at a time. If you give more than ten IDs, the IDs after 10th one are ignored. For more information, you can take a look at [http://developer.linkedin.com/docs/DOC-1044](http://developer.linkedin.com/docs/DOC-1044)

```python
result = api.send_message('This is a subject', 'This is the body')
if result is False:
    print api.get_error()
u'Missing {mailbox-item/recipients/recipient} element'
```

You can set the parameter **send_yourself** to True, so you can send the message to yourself.

```python
api.send_message('This is a subject', 'This is the body', ['ID1', 'ID2', 'ID3'], send_yourself=True)
```

You can send an invitation to your friend's email to invite them to join your LinkedIn network by simply calling **.send_invitation()** method.

```python
result = api.send_invitation('This is a subject', 'Join to my network', 'Ozgur', 'Vatansever', 'ozgurvt@gmail.com')
print result
True

result = api.send_invitation('This is a subject', 'Join to my network', 'Ozgur', 'Vatansever', 'ozgurvt')
if result is False:
    print api.get_error()
u'Invalid argument(s): {emailAddress=invalid_email [ozgurvt]}'
```

## Throttle Limits

LinkedIn API keys are throttled by default. You should take a look at [http://developer.linkedin.com/docs/DOC-1112](http://developer.linkedin.com/docs/DOC-1112) to get more information.