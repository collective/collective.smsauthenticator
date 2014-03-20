=============================================================
Simple example project for ``collective.smsauthenticator``
=============================================================
Installation instructions
-------------------------
Buildout
~~~~~~~~
$ python bootstrap.py -c buildout-base.cfg -v 1.7

$ ./bin/buildout -Nc buildout-dvl.cfg

$ ./bin/instance adduser admin@dev.example.com test

$ ./bin/instance fg

Create your Plone site
~~~~~~~~~~~~~~~~~~~~~~~
Then go to http://dev.example.com:8001 and create your Plone site.

Install the ``collective.smsauthenticator`` using ZMI quick-installer.

Create test user
~~~~~~~~~~~~~~~~
Go to http://dev.example.com:8001/Plone/@@usergroup-userprefs and create a
new user (let's assume test_user:test as login:password pair).

Open another browser or a new incognito/private window and opne your Plone
site. Find the login link and enter the test_user:test credentials.

Follow to the screenshots shown in the official documentation for further steps.
