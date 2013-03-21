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
This will print the authorization url to the screen. Go into that URL using a browser to grant access to the application. After you do so, the method will return with an API object you can now use.

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

## Connections API
The Connections API returns a list of **1st degree** connections for a user who has granted access to their account. For more information, you check out its [documentation](http://developers.linkedin.com/documents/connections-api).

To fetch your connections, you simply call **.get_connections()** method with proper GET querystring:

```python
application.get_connections()
{u'_total': 13,
 u'values': [{u'apiStandardProfileRequest': {u'headers': {u'_total': 1,
     u'values': [{u'name': u'x-li-auth-token', u'value': u'name:16V1033'}]},
    u'url': u'http://api.linkedin.com/v1/people/lddvGtD5xk'},
   u'firstName': u'John',
   u'headline': u'Ruby',
   u'id': u'2323SDFSsfd34',
   u'industry': u'Computer Software',
   u'lastName': u'DOE',
   u'location': {u'country': {u'code': u'tr'}, u'name': u'Istanbul, Turkey'},
   u'siteStandardProfileRequest': {u'url': u'http://www.linkedin.com/profile/view?id=049430532&authType=name&authToken=16V8&trk=api*a101945*s101945*'}},
   ....

application.get_connections(selectors=['headline, 'first-name', 'last-name'], params={'start':10, 'count':5})
```

## Search API
There are 2 types of Search APIs. One is the **People Search** API, second one is the **Company Search** API.

The People Search API returns information about people. It lets you implement most of what shows up when you do a search for "People" in the top right box on LinkedIn.com.
You can get more information from [here](http://developers.linkedin.com/documents/people-search-api).

```python
application.search_profile(selectors=[{'people': ['first-name', 'last-name']}], params={'keywords': 'apple microsoft'})
# Search URL is https://api.linkedin.com/v1/people-search:(people:(first-name,last-name))?keywords=apple%20microsoft

{u'people': {u'_count': 10,
  u'_start': 0,
  u'_total': 2,
  u'values': [
   {u'firstName': u'John', u'lastName': Doe'},
   {u'firstName': u'Jane', u'lastName': u'Doe'}
  ]}}
```

The Company Search API enables search across company pages. You can get more information from [here](http://developers.linkedin.com/documents/company-search).

```python
application.search_company(selectors=[{'companies': ['name', 'universal-name', 'website-url']}], params={'keywords': 'apple microsoft'})
# Search URL is https://api.linkedin.com/v1/company-search:(companies:(name,universal-name,website-url))?keywords=apple%20microsoft

{u'companies': {u'_count': 10,
  u'_start': 0,
  u'_total': 1064,
  u'values': [{u'name': u'Netflix',
    u'universalName': u'netflix',
    u'websiteUrl': u'http://netflix.com'},
   {u'name': u'Alliance Data',
    u'universalName': u'alliance-data',
    u'websiteUrl': u'www.alliancedata.com'},
   {u'name': u'GHA Technologies',
    u'universalName': u'gha-technologies',
    u'websiteUrl': u'www.gha-associates.com'},
   {u'name': u'Intelligent Decisions',
    u'universalName': u'intelligent-decisions',
    u'websiteUrl': u'http://www.intelligent.net'},
   {u'name': u'Mindfire Solutions',
    u'universalName': u'mindfire-solutions',
    u'websiteUrl': u'www.mindfiresolutions.com'},
   {u'name': u'Babel Media',
    u'universalName': u'babel-media',
    u'websiteUrl': u'http://www.babelmedia.com/'},
   {u'name': u'Milestone Technologies',
    u'universalName': u'milestone-technologies',
    u'websiteUrl': u'www.milestonepowered.com'},
   {u'name': u'Denali Advanced Integration',
    u'universalName': u'denali-advanced-integration',
    u'websiteUrl': u'www.denaliai.com'},
   {u'name': u'MicroAge',
    u'universalName': u'microage',
    u'websiteUrl': u'www.microage.com'},
   {u'name': u'TRUSTe',
    u'universalName': u'truste',
    u'websiteUrl': u'http://www.truste.com/'}]}}
```

## Group API
The Groups API provides rich access to read and interact with LinkedIn’s groups functionality. You can get more information from [here](http://developers.linkedin.com/documents/groups-api). By the help of the interface, you can fetch group details, get your group memberships as well as your posts for a specific group which you are a member of.

```python
application.get_group(41001)
{u'id': u'41001', u'name': u'Object Oriented Programming'}

application.get_memberships(params={'count': 20})
{u'_total': 1,
 u'values': [{u'_key': u'25827',
   u'group': {u'id': u'25827', u'name': u'Python Community'},
   u'membershipState': {u'code': u'member'}}]}

application.get_posts(41001)
```

You can also submit a new posts into a specific group.

```python
title = 'Scala for the Impatient'
summary = 'A new book has been published'
submitted_url = 'http://horstmann.com/scala/'
submitted_image_url = 'http://horstmann.com/scala/images/cover.png'
description = 'It is a great book for the keen beginners. Check it out!'

application.submit_group_post(41001, title, summary, submitted_url, submitted_image_url, description)
```

## Company API
The Company API:
 * Retrieves and displays one or more company profiles based on the company ID or universal name.
 * Returns basic company profile data, such as name, website, and industry.
 * Returns handles to additional company content, such as RSS stream and Twitter feed.

For more information, you can check out the documentation [here](http://developers.linkedin.com/documents/company-lookup-api-and-fields).


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