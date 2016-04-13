"""
Token validation. Here user is supposed to fill in the token received by SMS.
"""

import logging

from zope.schema import TextLine
from zope.i18nmessageid import MessageFactory

from z3c.form import button, field
from zope.i18n import translate

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage

from collective.smsauthenticator.helpers import (
    validate_mobile_number_authentication_code, validate_user_data, extract_request_data,
    get_updated_ips_for_member_properties_update, extract_request_data, send_login_code_sms,
    generate_code
    )

logger = logging.getLogger('collective.smsauthenticator')

DEBUG = False

_ = MessageFactory('collective.smsauthenticator')
from Products.CMFPlone import PloneMessageFactory as __

class ITokenForm(form.Schema):
    """
    Interface for the SMS Authenticator Token validation form.
    """
    token = TextLine(
        title=_('Enter code'),
        description=_('Enter the login code sent to your mobile number.'),
        required=False)


class TokenForm(form.SchemaForm):
    """
    Form for the SMS Authenticator Token validation. Any user that has two-step verification enabled,
    uses this form upon logging in.
    """
    fields = field.Fields(ITokenForm)
    ignoreContext = True
    schema = ITokenForm
    label = _(u'Two-step verification')
    description = _(u'Confirm your login by entering the login code sent to your mobile number by SMS.')
    css_class = "enableAutoFocus"

    def action(self):
        return "{0}?{1}".format(
            self.request.getURL(),
            self.request.get('QUERY_STRING', '')
            )

    @button.buttonAndHandler(_(u'Verify'))
    def handleSubmit(self, action):
        """
        Here we should check couple of things:

        - If the token provided is valid.
        - If the signature contains the user data needed (username and hash made of his data are valid).

        If all is well and valid, we sudo login the user given.
        """
        if not action.title == _(u'Verify'):
            return

        logger.debug('verify')

        data, errors = self.extractData()
        if errors:
            return False

        token = data.get('token', '')

        if not token:
            IStatusMessage(self.request).addStatusMessage(
                _("No token provided!"), 'error'
                )
            return

        user = None
        username = self.request.get('auth_user', '')

        if username:
            user = api.user.get(username=username)

            # Validating the signed request data. If invalid (likely throttled with or expired), generate an
            # appropriate error message.
            user_data_validation_result = validate_user_data(request=self.request, user=user)
            if not user_data_validation_result.result:
                if 'Signature timestamp expired!' in user_data_validation_result.reason:
                    # Remove used authentication code
                    user.setMemberProperties(
                        mapping = {
                            'mobile_number_authentication_code': '',
                            }
                        )
                IStatusMessage(self.request).addStatusMessage(
                    _("Invalid data. Details: {0}").format(' '.join(user_data_validation_result.reason)), 'error'
                    )
                return

        valid_token = validate_mobile_number_authentication_code(token, user=user)

        if valid_token:
            # We should login the user here
            self.context.acl_users.session._setupSession(str(username), self.context.REQUEST.RESPONSE)

            mapping = {'mobile_number_authentication_code': '',}
            mapping.update(get_updated_ips_for_member_properties_update(user))

            # Remove used authentication code and update the IPs list
            user.setMemberProperties(mapping=mapping)

            # TODO: Is there a nicer way of resolving the "@@sms_authenticator_token_form" URL?
            IStatusMessage(self.request).addStatusMessage(__("Welcome! You are now logged in."), 'info')
            request_data = extract_request_data(self.request)
            redirect_url = request_data.get('next_url', self.context.absolute_url())
            self.request.response.redirect(redirect_url)
        else:
            IStatusMessage(self.request).addStatusMessage(_("Invalid token or token expired."), 'error')

    @button.buttonAndHandler(_(u'Resend SMS'))
    def handleResendSMS(self, action):
        """
        Handle resend SMS action.
        """
        if not action.title == _(u'Resend SMS'):
            return

        logger.debug('resend sms')

        data, errors = self.extractData()
        #if errors:
        #    return False

        token = data.get('token', '')

        user = None
        username = self.request.get('auth_user', '')

        if username:
            user = api.user.get(username=username)

            # Validating the signed request data. If invalid (likely throttled with or expired), generate an
            # appropriate error message.
            user_data_validation_result = validate_user_data(request=self.request, user=user)
            if not user_data_validation_result.result:
                if 'Signature timestamp expired!' in user_data_validation_result.reason:
                    # Remove used authentication code
                    user.setMemberProperties(
                        mapping = {
                            'mobile_number_authentication_code': '',
                            }
                        )
                IStatusMessage(self.request).addStatusMessage(
                    _("Invalid data. Details: {0}").format(
                        ' '.join(user_data_validation_result.reason)
                     ),
                    'error'
                )
                return

        mobile_number_authentication_code = generate_code(user)
        mobile_number = user.getProperty('mobile_number')

        # Send the SMS
        sms_sent = send_login_code_sms(
            mobile_number = mobile_number,
            code = mobile_number_authentication_code
            )

        if sms_sent:
            # Save the `signature` value to the `mobile_number_reset_token`.
            user.setMemberProperties(
                mapping = {
                    'mobile_number_authentication_code': mobile_number_authentication_code,
                }
                )
            IStatusMessage(self.request).addStatusMessage(
                _("Your SMS has just been resent."), 'info'
                )

        self.request.response.redirect("{0}?{1}".format(self.request.ACTUAL_URL, self.request.QUERY_STRING))


    def updateFields(self, *args, **kwargs):
        """
        Here the following happens. Cookie set is cleared. Thus, user is no longer logged in, but only
        after his SMS Authenticator token has been validated.
        """
        logger.debug("Landed in the token hook.")

        request = self.request
        response = request['RESPONSE']
        if not request['REQUEST_METHOD'] == 'POST':
            response.setCookie('__ac', '', path='/')

        # Updating the description
        token_field = self.fields.get('token')
        if token_field:
            token_field.field.description = _(
                'token_field_description',
                default="""Enter the login code sent to your mobile number
If you have somehow lost your mobile number, request a reset
<a href='${absolute_url}/@@request-mobile-number-reset'>here</a>.
If you didn't receive an SMS message, resend it by clicking
the Resend SMS button below.""",
                mapping={'absolute_url': self.context.absolute_url()})

        return super(TokenForm, self).updateFields(*args, **kwargs)


# View for the ``TokenForm``.
TokenFormView = wrap_form(TokenForm)
