===========================
collective.smsauthenticator
===========================
`Two-step verification <http://en.wikipedia.org/wiki/Two-step_verification>`_
for Plone 4 with use login codes sent by SMS. This app allows users to enable
the two-step verification for their Plone accounts. A mobile phone capable to
receive SMS messages is obviously required. Usage of two-step verification is
optonal, unless site admins have forced it (configurable in app control panel).
Admins can white-list the IPs, for which the two-step verification would be
skipped.

Prerequiresites
===============
- Mobile phone which is able to receive SMS messages.
- Plone 4 (tested with Plone >= 4.3.1)

Limitations
===========
Note, that two-step verification works only for Plone users and does not work
for Zope users (those added with "./bin/instance" adduser command).

Usage
=====
Case 1: Enabling the two-step verification
------------------------------------------
Pre-conditions: User is not logged into the Plone site, does not yet have
two-step verification enabled and has a mobile phone.

From any page follow the "Enable two-step verification" link in the menu (next
to "Log out").

.. image:: _static/01_menu_enable.png
    :align: center

If you haven't yet filled in your mobile phone number, you will be requested to
do so. You will receive immeditely a SMS with confirmation code in.

.. image:: _static/02_setup_mobile_number.png
    :align: center

When you're done, you get to a page on which you will be requested to enter the
code received by SMS.

.. image:: _static/03_confirm_mobile_number_and_complete_two_step_verification_setup.png
    :align: center

Enter the secret code shown in the "Enter the verification code to activate
two-step verification" field for confirmation and press the "Verify" button.

Upon successful confirmation (you should see a message stating that) the
two-step verification is enabled for your account.

.. image:: _static/04_enable_two_step_verification_confirmation_message.png
    :align: center

Case 2: Two-step verification
-----------------------------
Pre-conditions: User is not logged in and has enabled the two-step verification.

When you log into the Plone site (just using username and password), you would
see an extra screen on which you are asked to provide the login code, sent to
your by SMS.

.. image:: _static/05_login_code_form.png
    :align: center

You should then check your phone for the new SMS message and type in the token
shown into the "Enter code" field.

If token is valid, you would be logged in.

Case 3: Lost mobile phone or phone number
-----------------------------------------
Pre-conditions: User is not logged in, has enabled the two-step verification.

There might be cases when you have lost your mobile phone (either really lost
it or broken accident or somehow lost ownership of your former mobile number).
For such cases, you can reset the phone number.

Log into the Plone site (just using username and password), for to see the extra
screen on which you are asked to provide the login code, sent to your by SMS
and follow the link (help text of the "Enter code" field). You would then land
on the page where from you can request the mobile number reset.

Enter your username and mobile number in the "Username" and "Mobile number"
fields respectively, press the "Submit" button. Link for resetting your mobile
number will appear in your mailbox shortly. Having clicked on the link to reset
the mobile number, would bring your to a page where you can enter the
verification code.

.. image:: _static/06_request_to_reset_mobile_number.png
    :align: center

You will receive an SMS with verification code shortly. Enter the code in the
"Enter the verification code to activate the two-step verification" field.


.. image:: _static/07_confirm_mobile_number_reset.png
    :align: center

Upon successful confirmation (you should see a message stating that) your
mobile number is reset.

.. image:: _static/08_mobile_number_reset_confirmation_message.png
    :align: center

Case 4: Disabling the two-step verification
-------------------------------------------
Pre-conditions: User is logged in and has enabled the two-step verification.

From any page follow the "Disable two-step verification" link in the menu (next
to "Log out").

.. image:: _static/09_menu_disable.png
    :align: center

After which you would get a message.

.. image:: _static/10_disable_two_step_verification_confirmation_message.png
    :align: center

Installation
============
Buildout
--------
>>> [instance]
>>> eggs +=
>>>     collective.smsauthenticator

>>> zcml +=
>>>     collective.smsauthenticator

ZMI
---
ZMI -> portal_quickinstaller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Choose "SMS Authenticator Plone" and install it.

ZMI -> acl_users
~~~~~~~~~~~~~~~~
1. Choose "sms_auth (SMS Authenticator plugin (collective.smsauthenticator))".

2. Make sure the "Active plugins" section of "Authentication" has the following
   plugins in the given order ("sms_auth" should come as first - critical!):

    - sms_auth
    - session
    - source_users

Configuration options
=====================
App control panel can be accessed at
http://your-plone-site.com/@@sms-authenticator-settings

Main
----

.. image:: _static/11_control_panel_tab_main.png
    :align: center

Globally enabled
~~~~~~~~~~~~~~~~
If checked, two-step verification is globally force-enabled for all site users
and they no longer have an option to disable it; this applies to all new users
(just registered accounts) as well.

White-listed IP addresses
~~~~~~~~~~~~~~~~~~~~~~~~~
List of white-listed IP addresses - one at a line. If user comes from one of
those, the two-step verification is skipped even if user has enabled it or
two-step verification is globally enabled.

Extra
~~~~~
Additionals options of the control panel are:

- Enable two-step verification for all users.
- Disable two-step verification for all users.

Twilio
------

.. image:: _static/12_control_panel_tab_twilio.png
    :align: center

Twilio number
~~~~~~~~~~~~~
Your `Twilio <https://www.twilio.com/>`_ AccountSID and AuthToken. Visit your
Twilio `Account Phone Number
<https://www.twilio.com/user/account/phone-numbers/incoming>`_ page and check
the `Manage Numbers` section.

Twilio AccountSID and Twilio AuthToken
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Your `Twilio <https://www.twilio.com/>`_ AccountSID and AuthToken. Visit your
Twilio `Account Settings <https://www.twilio.com/user/account/settings>`_ page
and check the `API Credentials` section.

Security
--------

.. image:: _static/13_control_panel_tab_security.png
    :align: center

Secret Key
~~~~~~~~~~
Site secret key - can be any string. See it as some sort of a password.

Token lifetime
~~~~~~~~~~~~~~
Lifetime of the login- and the mobile number reset- codes. Defaults to 5
minutes (300 seconds).

Notes
=====
It's important that SMS Authenticator comes as first in the
ZMI -> acl_users -> Authentication.

Tested in combination with the following products:

- The `Products.LoginLockout
  <https://pypi.python.org/pypi/Products.LoginLockout>`_.
  `SMSAuthenticator` comes as first, `LoginLockout` as second. All works fine.

Documentation
=============
See the documentation at:

- http://collectivesmsauthenticator.readthedocs.org/en/latest/
- http://pythonhosted.org/collective.smsauthenticator/

Support
=======
For feature requests or bugs, open an issue. For questions, send us an email to
info@gw20e.com.

License
=======
GPL 2.0

Authors & Copyright
===================
Copyright (C) 2014 `Goldmund, Wyldebeast & Wunderliebe <http://www.goldmund-wyldebeast-wunderliebe.nl/>`_.

Authors are listed in alphabetic order (by name):

- Artur Barseghyan [barseghyanartur]
- Harald Friessnegger[frisi]
- Jan Murre [JJM]
- Rene Jochum [pcdummy]
- Peter Uittenbroek [puittenbroek]

TODOs and Roadmap
=================
See `TODOS.rst <https://raw.github.com/collective/collective.smsauthenticator/master/TODOS.rst>`_
file for the list of TODOs.

