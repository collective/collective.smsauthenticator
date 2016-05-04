"""
Reset bar-code. This is the place where the new number is actually set (upon confirmation). First of
all upon landing on the page (GET request) the validity of the URL is checked, since it's signed
and has an expiration limit of 10 minutes. The phone number to be added to users' profile is
taken from the GET request as well, but no worries - it's signed too, thus, in case of data tumpering,
the entire signature would become invalid. Note, that signature used for resetting the mobile number is
written to the users' profile on the moment request is sent. No unauthorised reproduction is possible,
since we match it to the one in users' profile.

If all things mentioned above are in good order, user would see a form where he can fill in the
verification code received by SMS. That code had been stored in users' profile too and is simply
matched the one filled in.

If all checks pass well, the mobile number is definitely set in users' profile.
"""
import logging

from zope.i18nmessageid import MessageFactory

from z3c.form import button, field

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage
from zope.schema import TextLine

from collective.smsauthenticator.helpers import validate_mobile_number_reset_code, validate_user_data

logger = logging.getLogger('collective.smsauthenticator')

_ = MessageFactory('collective.smsauthenticator')


class IResetMobileNumberForm(form.Schema):
    """
    Interface for the SMS Authenticator Reset Mobile Number form.
    """
    token = TextLine(
        title=_(u"SMS verification code"),
        description=_(u"Enter the verification code you received on your mobile phone."),
        required=True
    )


class ResetMobileNumberForm(form.SchemaForm):
    """
    Form for the resetting the mobile number.

    What happens here is:

    - Signed user data is validated. If valid, the user is fetched.
    - Token (`signature` param) is matched to the one obtained from user records. If matched, the
      mobile number saved in the users' profile.
    """
    fields = field.Fields(IResetMobileNumberForm)
    ignoreContext = True
    schema = IResetMobileNumberForm
    label = _("(Re)set your two-step verification mobile number")
    description = _(u"You have received (or will shortly receive) an SMS with an verification code.\
        <br/>After successfully submitting this form, you will be automatically logged in.")
    css_class = "enableAutoFocus"

    def action(self):
        return "{0}?{1}".format(
            self.request.getURL(),
            self.request.get('QUERY_STRING', '')
            )

    @button.buttonAndHandler(_('Verify'))
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        # Mobile number specified as a new phone number
        mobile_number = self.request.get('mobile_number', '')

        # Token entered by user from his mobile device sent to him by SMS
        token = data.get('token', '')

        # Signature token generated for resetting the bar code.
        signature_token = self.request.get('signature', '')
        valid_until = self.request.get('valid_until', '')

        username = self.request.get('auth_user', '')
        user = api.user.get(username=username)

        if not user:
            reason = _("User not found {0}.").format(username)
            IStatusMessage(self.request).addStatusMessage(
                _("(Re)setting of the mobile number failed! {0}").format(reason),
                'error'
                )
            return

        # Validating the SMSAuthenticator app token
        valid_token = validate_mobile_number_reset_code(token, user=user)

        reason = None
        if valid_token:
            try:
                # Checking if token generated for resetting the bar code image is equal
                # to the one taken from current request.
                mobile_number_reset_token = user.getProperty('mobile_number_reset_token')
                if mobile_number_reset_token != signature_token:
                    reason = _("Invalid mobile number reset token.")
                    IStatusMessage(self.request).addStatusMessage(
                        _("(Re)setting of the mobile number failed! {0}").format(reason),
                        'error')
                    return

                user.setMemberProperties(
                    mapping = {
                        'enable_two_step_verification': True,
                        'mobile_number': mobile_number,
                        'mobile_number_reset_token': '',
                        'mobile_number_reset_code': ''
                        }
                    )

                IStatusMessage(self.request).addStatusMessage(
                    _("You have successfully changed/set your mobile number.\
                      You're now logged in."),
                    'info'
                    )
                redirect_url = "{0}".format(self.context.absolute_url())

                # Logging user in
                self.context.acl_users.session._setupSession(username, self.request.response)

                # Redirect user to home
                self.request.response.redirect(redirect_url)
            except Exception as e:
                reason = _(str(e))
        else:
            reason = _("Invalid token or token expired.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(_("Setup failed! {0}").format(reason), 'error')

    def updateFields(self, *args, **kwargs):
        """
        Here happens the following:

        - Signed user data is validated. If valid, the user is fetched.
        - Token (`signature` param) is matched to the one obtained from user records. If matched, the
          mobile number is reset (and saved in the users' profile).
        """
        username = self.request.get('auth_user', '')
        token = self.request.get('signature', '')
        user = api.user.get(username=username)

        # If valid user
        if user:
            # Getting the users' mobile number reset token saved in his profile.
            mobile_number_reset_token = user.getProperty('mobile_number_reset_token')

            # Validate the user data
            user_data_validation_result = validate_user_data(request=self.request, user=user)

            # If all goes well, save the number in profile (overwrite_secret=True).
            if not user_data_validation_result.result:
                IStatusMessage(self.request).addStatusMessage(
                    ' '.join(user_data_validation_result.reason),
                    'error'
                    )
            if mobile_number_reset_token != token:
                IStatusMessage(self.request).addStatusMessage(
                    _("Invalid mobile number reset token"),
                    'error'
                    )

        return super(ResetMobileNumberForm, self).updateFields(*args, **kwargs)


# View for the ``ResetMobileNumberForm``.
ResetMobileNumberFormView = wrap_form(ResetMobileNumberForm)
