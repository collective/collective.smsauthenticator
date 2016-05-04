"""
The helper module contains various methods for api security
"""
from collective.smsauthenticator.browser.controlpanel\
    import ISMSAuthenticatorSettings
from Globals import DevelopmentMode
from hashlib import sha1
from plone import api
from plone.registry.interfaces import IRegistry
from random import randint
from ska import sign_url, validate_signed_request_data
from twilio.rest import TwilioRestClient
from twilio.rest.exceptions import TwilioRestException as TwilioException
from urllib import unquote, quote
from urlparse import urlparse
from uuid import uuid4
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

import logging
import rebus
import time

_ = MessageFactory('collective.smsauthenticator')

logger = logging.getLogger("collective.smsauthenticator")

# ******************************************


def get_app_settings():
    """
    Gets the SMS Authenticator settings.
    """
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISMSAuthenticatorSettings, check=False)
    return settings


def get_user(username):
    """
    Get user by username given and return member object.
    """
    return api.user.get(username=username)


def get_username(user=None):
    """
    Gets the username of the user.

    :param user: If given, used to extract the user. Otherwise,
        ``plone.api.user.get_current`` is used.
    :return string:
    """
    if user is None:
        user = api.user.get_current()
    if user:
        return user.getUserName()


def get_base_url(request=None):
    """
    Gets domain name (with HTTP).

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if request is None:
        request = getRequest()

    parsed_uri = urlparse(request.base)
    return "{0}://{1}/".format(parsed_uri.scheme, parsed_uri.netloc)


def get_domain_name(request=None):
    """
    Gets domain name (without HTTP).

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if request is None:
        request = getRequest()

    parsed_uri = urlparse(request.base)
    return parsed_uri.netloc


def generate_secret(user):
    """
    Generates secret for the user.

    :param Products.PlonePAS.tools.memberdata user:
    """
    secret = rebus.b32encode(str(uuid4()))
    user.setMemberProperties(mapping={'two_step_verification_secret': secret})
    return secret


def get_secret(user=None, hashed=False):
    """
    Gets users' secret code. If ``hashed`` is set to True, returned hashed.

    :param Products.PlonePAS.tools.memberdata user:
    :param bool hashed: If set to True, hashed version is returned.
    :return string:
    """
    # TODO: Return hashed version if ``hashed`` is set to True.
    if user is None:
        user = api.user.get_current()
    if user:
        secret = user.getProperty('two_step_verification_secret')

        # If string returned, then it's likely a set string
        if isinstance(secret, basestring) and secret:
            return secret


def get_or_create_secret(user, overwrite=False):
    """
    Gets or creates token secret for the user given. Checks first if user given
     has a ``secret`` generated. If not, generate it for him and save it in his
      profile (``two_step_verification_secret``).

    :param Products.PlonePAS.tools.memberdata user: If provided, used.
        Otherwise ``plone.api.user.get_current`` is used to obtain the user.
    :return string:
    """
    # TODO: Return hashed version if ``hashed`` is set to True.
    if user is None:
        user = api.user.get_current()

    if overwrite:
        return generate_secret(user)

    secret = user.getProperty('two_step_verification_secret')
    if isinstance(secret, basestring) and secret:
        return secret
    else:
        return generate_secret(user)


def generate_code(user, length=6):
    """
    Gets a random token to reset the mobile number (time based) + random char.

    :param Products.PlonePAS.tools.memberdata user:
    :param int length:
    :return string:
    """
    secret = get_or_create_secret(user)
    return sha1("{0}{1}{2}".format(
        str(uuid4()), str(randint(0, 9)), secret)).hexdigest()[:8]


def validate_code(code, prop, user=None):
    """
    Validates the given code by matching it with one stored in users' profile.

    :param string code:
    :param string prop:
    :param Products.PlonePAS.tools.memberdata user:
    :return bool:
    """
    if user is None:
        user = api.user.get_current()

    stored_code = user.getProperty(prop)

    return stored_code == code


def validate_mobile_number_reset_code(code, user=None):
    return validate_code(code=code, prop='mobile_number_reset_code', user=user)


def validate_mobile_number_authentication_code(code, user=None):
    return validate_code(code=code, prop='mobile_number_authentication_code',
                         user=user)


def get_browser_hash(request=None):
    """
    Gets browser hash. Adds an extra security layer,
     since browser version is unlikely to be changed.

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if request is None:
        request = getRequest()

    try:
        return sha1(request.get('HTTP_USER_AGENT')).hexdigest()
    except Exception as e:
        logger.debug(str(e))
        return ''


def get_ska_secret_key(request=None, user=None, use_browser_hash=True):
    """
    Gets the `secret_key` to be used in `ska` package.

    - Value of the ``two_step_verification_secret`` (from users' profile).
    - Browser info (hash of)
    - The SECRET set for the `ska` (use `plone.app.registry`).

    :param ZPublisher.HTTPRequest request:
    :param Products.PlonePAS.tools.memberdata user:
    :param bool use_browser_hash: If set to True, browser hash is used.
        Otherwise - not. Defaults to True.
    :return string:
    """
    if request is None:
        request = getRequest()

    if user is None:
        user = api.user.get_current()

    settings = get_app_settings()

    ska_secret_key = settings.ska_secret_key

    user_secret = user.getProperty('two_step_verification_secret')

    if use_browser_hash:
        browser_hash = get_browser_hash(request=request)
    else:
        browser_hash = ''

    return "{0}{1}{2}".format(user_secret, browser_hash, ska_secret_key)


def is_two_step_verification_globally_enabled():
    """
    Checks if the two-step verification is globally enabled.

    :return bool:
    """
    settings = get_app_settings()
    return settings.globally_enabled


def get_ska_token_lifetime(settings=None):
    """
    Gets the `ska` token lifetime (in seconds) from settings.

    :return int:
    """
    if settings is None:
        settings = get_app_settings()

    return settings.ska_token_lifetime


def sign_user_data(request=None, user=None, url='@@sms-authenticator-token'):
    """
    Signs the user data with `ska` package. The secret key is `secret_key`
     to be used with `ska` is a combination of:

    - Value of the ``two_step_verification_secret`` (from users' profile).
    - Browser info (hash of)
    - The SECRET set for the `ska` (use `plone.app.registry`).

    :param ZPublisher.HTTPRequest request:
    :param Products.PlonePAS.tools.memberdata user:
    :param string url:
    :return string:
    """
    if request is None:
        request = getRequest()

    if user is None:
        user = api.user.get_current()

    token_lifetime = get_ska_token_lifetime()

    # Make sure the secret key always exists
    get_or_create_secret(user)

    secret_key = get_ska_secret_key(request=request, user=user)
    signed_url = sign_url(
        auth_user=user.getUserId(),
        secret_key=secret_key,
        url=url,
        lifetime=token_lifetime
    )
    return signed_url


def extract_request_data_from_query_string(request_qs):
    """
    Plone seems to strip/escape some special chars (such as '+') from values
     and those chars are quite important for us. This method extracts the
     vars from request QUERY_STRING given and returns them unescaped.

    :FIXME: As stated above, for some reason Plone escapes from special chars
     from the values. If you know what the reason is and if it has some effects
     on security, please make the changes
    necessary.

    :param string request_qs:
    :return dict:
    """
    request_data = {}

    if not request_qs:
        return request_data

    for part in request_qs.split('&'):
        try:
            key, value = part.split('=', 1)
            request_data.update({key: unquote(value)})
        except ValueError:
            pass

    return request_data


def extract_request_data(request):
    """
    Plone seems to strip/escape some special chars (such as '+') from values
     and those chars are quite important for us.
     This method extracts the vars from request
     QUERY_STRING given and returns them unescaped.

    :FIXME: As stated above, for some reason Plone escapes from special chars
     from the values. If you know what the reason is and if it has some effects
     on security, please make the changes necessary.

    :param request ZPublisher.HTTPRequest:
    :return dict:
    """
    request_qs = request.get('QUERY_STRING')
    return extract_request_data_from_query_string(request_qs)


def extract_next_url_from_referer(request, quote_url=False):
    """
    Since we override the default Plone functionality (take out the `came_from`
     from the login form for a very strong reason), we want to make sure that
     for users, the "came from" functionality stays intact. That why, we check
     the referer for the `came_from` attributes and if present, redirect to
     that after successful two-step verification token validation.
    :param request ZPublisher.HTTPRequest:
    :return string: Extracted `came_from` URL.
    """
    referer = request.get('HTTP_REFERER')
    request_qs = urlparse(referer).query
    request_data = extract_request_data_from_query_string(request_qs)
    url = request_data.get('came_from', '')

    if quote_url:
        return quote(url)

    return url


def validate_user_data(request, user, use_browser_hash=True):
    """
    Validates the user data.

    :param ZPublisher.HTTPRequest request:
    :param Products.PlonePAS.tools.memberdata user:
    :return ska.SignatureValidationResult:
    """
    secret_key = get_ska_secret_key(request=request, user=user,
                                    use_browser_hash=use_browser_hash)
    validation_result = validate_signed_request_data(
        data=extract_request_data(request),
        secret_key=secret_key
        )
    return validation_result


def has_enabled_two_step_verification(user):
    """
    Checks if user has enabled the two-step verification.

    :param Products.PlonePAS.tools.memberdata user:
    :return bool:
    """
    if bool(api.user.is_anonymous()) is True:
        return None

    try:
        return user.getProperty('enable_two_step_verification', False)
    except Exception:
        return None


def enable_two_step_verification_for_users(users=[]):
    """
    Enable two-step verification for the list of users given.
    """
    if not users:
        users = api.user.get_users()

    for user in users:
        try:
            get_or_create_secret(user)
            if not has_enabled_two_step_verification(user):
                user.setMemberProperties(
                    mapping={'enable_two_step_verification': True})
        except Exception as e:
            logger.debug(str(e))


def disable_two_step_verification_for_users(users=[]):
    """
    Disable two-step verification for the list of users given.
    """
    if not users:
        users = api.user.get_users()

    for user in users:
        try:
            # get_or_create_secret(user)
            if has_enabled_two_step_verification(user):
                user.setMemberProperties(
                    mapping={
                        'enable_two_step_verification': False,
                        'two_step_verification_secret': '',
                        'mobile_number_reset_token': '',
                        'mobile_number_reset_code': '',
                        'mobile_number_authentication_code': '',
                    }
                    )
        except Exception as e:
            logger.debug(str(e))


def extract_ip_address_from_request(request=None):
    """
    Extracts client's IP address from request. This is not the safest solution,
     since client may change headers.

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if not request:
        request = getRequest()

    PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )
    ip = request.get('REMOTE_ADDR')
    x_forwarded_for = request.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        proxies = [proxy.strip() for proxy in x_forwarded_for.split(',')]

        # Remove the private ips from the beginning
        while (len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)

        # Take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip


def get_whitelist(name='ip_addresses_whitelist'):
    """ Get the whitelist with the given name

    :param str name: Name of the whitelist
    :return list: The whitelist
    """
    settings = get_app_settings()
    white_list = getattr(settings, name, "")
    if white_list:
        # Split into list
        white_list = white_list.split("\n")
        # Strip all values
        white_list = [x.strip() for x in white_list]
        # Check for empties
        white_list = [y for y in white_list if y]
    else:
        white_list = []
    return white_list


def is_whitelisted_client(request=None, user=None):
    """
    Checks if client's IP address is whitelisted.

    :param ZPublisher.HTTPRequest request:
    :return bool:
    """
    ip_addresses_whitelist = get_whitelist()
    user_whitelist = get_whitelist("user_whitelist")

    ip_address = extract_ip_address_from_request(request=request)

    if ip_address in ip_addresses_whitelist:
        return True

    if user and user.id in user_whitelist:
        return True

    return False


def send_sms(mobile_number, message):
    """
    Sends an SMS to the monile number given for mobile number
     reset confirmation.

    :param string mobile_number:
    :param string message: Message.
    :return bool: True on success and False on failure.
    """
    settings = get_app_settings()

    sms_client = TwilioRestClient(settings.twilio_account_sid,
                                  settings.twilio_auth_token)

    language = api.portal.get_default_language()
    user = api.user.get_current()
    if user.getProperty('language'):
        language = user.getProperty('language')

    message = translate(message, target_language=language)
    try:
        sms_client.messages.create(
           to=mobile_number,
           from_=settings.twilio_number,
           body=message.encode('UTF-8')
           )
        return True
    except TwilioException as e:
        # Log in the error_log
        logger.exception(e)
        return False


def send_mobile_number_reset_confirmation_code_sms(mobile_number, code):
    """
    Sends an SMS to the monile number given for mobile
     number reset confirmation.

    :param string mobile_number:
    :param string code:
    :return bool: True on success and False on failure.
    """
    message = _("Use this code to confirm your mobile phone reset: ${code}", mapping={'code': code})
    return send_sms(mobile_number, message)


def send_login_code_sms(mobile_number, code):
    """
    Sends an SMS to the monile number given for mobile
     number reset confirmation.

    :param string mobile_number:
    :param string code:
    :return bool: True on success and False on failure.
    """
    message = _("Use this code to login: ${code}", mapping={'code': code})
    return send_sms(mobile_number, message)


def send_mobile_number_setup_confirmation_code_sms(mobile_number, code):
    """
    Sends an SMS to the monile number given for mobile
     number setup confirmation.

    :param string mobile_number:
    :param string code:
    :return bool: True on success and False on failure.
    """
    message = _("Use this code to confirm your mobile phone setup: ${code}", mapping={'code': code})
    return send_sms(mobile_number, message)


def get_updated_ips_for_member_properties_update(user, request=None):
    """
    Save IP, from which user is logged in, into the system.

    :param Products.PlonePAS.tools.memberdata user:
    :param ZPublisher.HTTPRequest request:
    :return bool: True on success and False on failure.
    """
    ip = extract_ip_address_from_request(request)
    existing_ips = user.getProperty('ips', '')
    if existing_ips:
        updated_ips = "{0}\n{1},{2}".format(existing_ips, ip, time.time())
    else:
        updated_ips = "{1},{2}".format(existing_ips, ip, time.time())
    return {'ips': updated_ips}


def save_ip(user, request=None):
    """
    Save IP, from which user is logged in, into the system.

    :param Products.PlonePAS.tools.memberdata user:
    :param ZPublisher.HTTPRequest request:
    :return bool: True on success and False on failure.
    """
    mapping = get_updated_ips_for_member_properties_update(
        user=user, request=request)

    try:
        user.setMemberProperties(mapping=mapping)
        return True
    except Exception:
        return False
