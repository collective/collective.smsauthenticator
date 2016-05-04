"""
Request the mobile number reset. What actually happens here, is that user provides his username
and a mobile number. After that an confirmation email is sent to users' email address (taken
from the profile). Also, an SMS message with code to reset the mobile number is immediately
sent to the phone number given. No other information is specified in the SMS. Once user checks
his email and follows the link given, he lands on the page on which he is supposed to fill in the
verification code received by SMS. Upon successful validation, the mobile number is reset.
"""
import logging
from smtplib import SMTPRecipientsRefused

from six import text_type

from zope.i18nmessageid import MessageFactory
from zope.schema import TextLine
from z3c.form import button, field

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from ska import Signature, RequestHelper

from collective.smsauthenticator.helpers import (
    get_ska_secret_key, generate_code, send_mobile_number_reset_confirmation_code_sms,
    get_ska_token_lifetime
    )

logger = logging.getLogger('collective.smsauthenticator')

_ = MessageFactory('collective.smsauthenticator')


class IRequestMobileNumberResetForm(form.Schema):
    """
    Interface for the request to reset the SMS Authenticator mobile number form.
    """
    username = TextLine(
        title=_(u'Username'),
        description=_(u'Enter your username for verification.'),
        required=True
    )
    mobile_number = TextLine(
        title=_(u'Mobile number'),
        description=_(u"Enter your mobile phone number. Use the international format.\
            <br/>Example Dutch number: +31699555555\
            <br/>Example International number: +49234555776"),
        required=True
    )
    form.mode(note='display')
    note = TextLine(
            title=_(u"Important note"),
            default=u"",
            readonly=True,
            required=False,
            description=_(u"After submitting this form, you will receive an e-mail with a link and a SMS with a code. \
    <br/><br/> To successfully verify your mobile number, open the link from your e-mail in a browser and enter the code from your SMS in the form.")
        )


class RequestMobileNumberResetForm(form.SchemaForm):
    """
    Form for request to reset to the SMS Authenticator mobile number form.
    """
    fields = field.Fields(IRequestMobileNumberResetForm)
    ignoreContext = True
    schema = IRequestMobileNumberResetForm
    label = _("Request to (re)set the mobile number")
    description = _(u"Use the form below to (re)set your mobile phone number.")
    css_class = "enableAutoFocus"

    @button.buttonAndHandler(_('Submit'))
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        username = data.get('username', '')
        mobile_number = data.get('mobile_number', '')

        user = api.user.get(username=username)

        reason = None
        if user:
            try:
                # Here we need to generate a token which is valid for let's say, 2 hours
                # using which it should be possible to reset the mobile number. The `signature`
                # generated should be saved in the user profile `mobile_number_reset_token`.
                ska_secret_key = get_ska_secret_key(request=self.request, user=user)

                # We also need to generate another token (no security, just a random string)
                # to sent to users' mobile number.
                mobile_number_reset_code = generate_code(user)

                token_lifetime = get_ska_token_lifetime()

                signature = Signature.generate_signature(
                    auth_user = username,
                    secret_key = ska_secret_key,
                    lifetime = token_lifetime,
                    extra = {'mobile_number': mobile_number}
                    )

                request_helper = RequestHelper(
                    signature_param = 'signature',
                    auth_user_param = 'auth_user',
                    valid_until_param = 'valid_until'
                    )

                signed_url = request_helper.signature_to_url(
                    signature = signature,
                    endpoint_url = '{0}/{1}'.format(self.context.absolute_url(), '@@reset-mobile-number')
                )

                # Send the SMS
                sms_sent = send_mobile_number_reset_confirmation_code_sms(
                    mobile_number = mobile_number,
                    code = mobile_number_reset_code
                    )

                if not sms_sent:
                    IStatusMessage(self.request).addStatusMessage(
                        _("An error occured while sending the SMS to the number specified."),
                        'info'
                        )
                    redirect_url = "{0}".format(self.context.absolute_url())
                    self.request.response.redirect(redirect_url)
                    return

                # Save the `signature` value to the `mobile_number_reset_token`.
                user.setMemberProperties(
                    mapping = {
                        'mobile_number_reset_token': str(signature),
                        'mobile_number_reset_code': mobile_number_reset_code,
                        'mobile_number_authentication_code': '',
                        }
                    )

                # Now we need to send an email to user with URL in and a small explanations.
                try:
                    host = getToolByName(self, 'MailHost')

                    mail_text_template = self.context.restrictedTraverse('request_mobile_number_reset_email')
                    mail_text = mail_text_template(
                        member = user,
                        mobile_number_reset_url = signed_url,
                        charset = 'utf-8'
                        )
                    mail_text = mail_text.format(mobile_number_reset_url=signed_url)

                    host.send(
                        mail_text.encode('UTF-8'),
                        immediate = True,
                        msg_type = 'text/html'
                        )
                except SMTPRecipientsRefused as e:
                    raise SMTPRecipientsRefused('Recipient address rejected by server')

                IStatusMessage(self.request).addStatusMessage(
                    _("An email with further instructions for (re)setting your mobile number has been sent."),
                    'info'
                    )
                redirect_url = "{0}/@@reset-email-sent".format(self.context.absolute_url())
                self.request.response.redirect(redirect_url)
            except ValueError as e:
                reason = _(str(e))
        else:
            reason = _("Invalid username.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(
                _("Request for mobile number reset is failed! {0}").format(reason),
                'error'
                )

    def updateFields(self, *args, **kwargs):
        """
        """
        request = self.request
        response = request['RESPONSE']
        response.setCookie('__ac', '', path='/')

        # Setting the value from get "username" value if available.
        username_field = self.fields.get('username')
        if request.get('username'):
            username_field.field.default = text_type(request.get('username'))

        return super(RequestMobileNumberResetForm, self).updateFields(*args, **kwargs)


# View for the ``RequestMobileNumberResetForm``.
RequestMobileNumberResetFormView = wrap_form(RequestMobileNumberResetForm)
