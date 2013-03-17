# Python LinkedIn

Python interface to the LinkedIn API

[![LinkedIn](http://developer.linkedin.com/sites/default/files/LinkedIn_Logo60px.png)](http://developer.linkedin.com)

This library provides a pure python interface for the LinkedIn **Connection**, **Profile**, **Search**, **Status**, **Messaging** and **Invitation** APIs.

[LinkedIn](http://developer.linkedin.com) provides a service that lets people bring their LinkedIn profiles and networks with them to your site or application via their OAuth based API. This library provides a lightweight interface over a complicated LinkedIn OAuth based API to make it for python programmers easy to use.

## Installation

[![Build Status](https://travis-ci.org/ozgur/python-linkedin.png?branch=master)](https://travis-ci.org/ozgur/python-linkedin)

You can install **python-linkedin** library via pip:

    $ pip install python-linkedin

## API Keys

In order to use the LinkedIn API, you have an **application key** and **application secret**. For debugging purposes I can provide you those. You can use the following as api key and secret:

```python
KEY = 'wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl'
SECRET = 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG'
```

You can also get those keys from [here](http://developer.linkedin.com/rest).


## Quick Usage From Python Interpreter

For testing the library using an interpreter, use the quick helper.

```python
from linkedin import helper
api = helper.quick_api(<Your KEY>, <Your SECRET>)
```

This will print a url to the screen. Go into this URL using a browser, after you login, the method will return with an API object you can now use.

```python
api.get_profile()
```

## Usage

You can use **http://localhost** as the return url. Return URL is a url where LinkedIn redirects the user after he/she grants access to your application.

```python
from linkedin import linkedin

RETURN_URL = 'http://localhost'
api = linkedin.LinkedIn(<Your KEY>, <Your SECRET>, RETURN_URL)
result = api.request_token()
if result is True:
    api.get_authorize_url() # open this url on your browser
```

When you grant access to the application, you will be redirected to the return url with the following query strings appended to your RETURN_URL:

```python
"http://localhost/?oauth_token=0b27806e-feec-41d4-aac5-619ba43770f1&oauth_verifier=04874"
```

This means that the **auth_verifier** value is 04874. After you get the verifier, you call the **.access_token()** method to get the access token.

```python
result = api.access_token(verifier='04874')
if result is True:
    profile = api.get_profile()
    print profile.id
```

If you know your public url, call the method above with your public url for more information.

```python
profile = api.get_profile(member_id=None, url='http://www.linkedin.com/in/ozgurv')
print profile.id, profile.first_name, profile.last_name, profile.picture_url
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