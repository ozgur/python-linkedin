Python LinkedIn
=================

Python interface to the LinkedIn API

This library provides a pure Python interface to the LinkedIn **Profile**, **Group**, **Company**, **Jobs**, **Search**, **Share**, **Network** and **Invitation** REST APIs.

`LinkedIn <http://developer.linkedin.com>`_ provides a service that lets people bring their LinkedIn profiles and networks with them to your site or application via their OAuth based API. This library provides a lightweight interface over a complicated LinkedIn OAuth based API to make it for python programmers easy to use.

Installation
--------------------

You can install **python-linkedin** library via pip:

.. code-block:: bash

    $ pip install python-linkedin

Authentication
-----------------------

LinkedIn REST API uses **Oauth 2.0** protocol for authentication. In order to use the LinkedIn API, you have an **application key** and **application secret**. You can get more detail from `here <http://developers.linkedin.com/documents/authentication>`_.

For debugging purposes you can use the credentials below. It belongs to my test application. Nothing's harmful.

.. code-block:: python

    KEY = 'wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl'
    SECRET = 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG'


LinkedIn redirects the user back to your website's URL after granting access (giving proper permissions) to your application. We call that url **RETURN URL**. Assuming your return url is **http://localhost:8000**, you can write something like this:

.. code-block:: python

    from linkedin import linkedin

    API_KEY = "wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl"
    API_SECRET = "daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG"
    RETURN_URL = "http://localhost:8000"
    # Optionally one can send custom "state" value that will be returned from OAuth server
    # It can be used to track your user state or something else (it's up to you)
    # Be aware that this value is sent to OAuth server AS IS - make sure to encode or hash it
    #authorization.state = 'your_encoded_message'
    authentication = linkedin.LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL, linkedin.PERMISSIONS.enums.values())
    print authentication.authorization_url
    application = linkedin.LinkedInApplication(authentication)

When you grant access to the application, you will be redirected to the return url with the following query strings appended to your **RETURN_URL**:

.. code-block:: python

    "http://localhost:8000/?code=AQTXrv3Pe1iWS0EQvLg0NJA8ju_XuiadXACqHennhWih7iRyDSzAm5jaf3R7I8&state=ea34a04b91c72863c82878d2b8f1836c"


This means that the value of the **authorization_code** is **AQTXrv3Pe1iWS0EQvLg0NJA8ju_XuiadXACqHennhWih7iRyDSzAm5jaf3R7I8**. After setting it by hand, we can call the **.get_access_token()** to get the actual token.

.. code-block:: python

    authentication.authorization_code = "AQTXrv3Pe1iWS0EQvLg0NJA8ju_XuiadXACqHennhWih7iRyDSzAm5jaf3R7I8"
    authentication.get_access_token()


After you get the access token, you are now permitted to make API calls on behalf of the user who granted access to you app. In addition to that, in order to prevent from going through the OAuth flow for every consecutive request,
one can directly assign the access token obtained before to the application instance.


.. code-block:: python

    application = linkedin.LinkedInApplication(token='AQTFtPILQkJzXHrHtyQ0rjLe3W0I')


Quick Usage From Python Interpreter
---------------------------------------------------------

For testing the library using an interpreter, use the quick helper.

.. code-block:: python

    from linkedin import server
    application = server.quick_api(KEY, SECRET)

This will print the authorization url to the screen. Go into this URL using a browser, after you login, the method will return with an API object you can now use.

.. code-block:: python

    application.get_profile()


More
-----------------
For more information, visit the `homepage <http://ozgur.github.com/python-linkedin/>`_ of the project.
