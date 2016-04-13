"""
User setup. Here user himself sets the two-step verification.
"""

import logging

from zope.i18nmessageid import MessageFactory

from z3c.form import button, field

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage
from zope.schema import TextLine

from collective.smsauthenticator.helpers import validate_mobile_number_reset_code, get_or_create_secret

logger = logging.getLogger('collective.smsauthenticator')

_ = MessageFactory('collective.smsauthenticator')


class ISetupTwoStepVerificationForm(form.Schema):
    """
    Interface for the SMS Authenticator setup form.
    """
    token = TextLine(
        title=_(u"Enter the verification code to activate two-step verification "),
        description=_(u"You should have received an SMS message to the mobile number specified. "
                      u"Please, enter the code below."),
        required=True
    )


class SetupTwoStepVerificationForm(form.SchemaForm):
    """
    Form for the SMS Authenticator setup.
    """
    fields = field.Fields(ISetupTwoStepVerificationForm)
    ignoreContext = True
    schema = ISetupTwoStepVerificationForm
    label = _("Setup two-step verification")
    description = _(u"Complete the two-step verification setup by confirming your mobile number")
    css_class = "enableAutoFocus"

    @button.buttonAndHandler(_('Verify'))
    def handleSubmit(self, action):
        if bool(api.user.is_anonymous()) is True:
            self.request.response.setStatus(401, _('Forbidden for anonymous'), True)
            return False

        data, errors = self.extractData()
        if errors:
            return False

        token = data.get('token', '')

        user = api.user.get_current()

        # Validating the SMSAuthenticator app token
        valid_token = validate_mobile_number_reset_code(token, user=user)

        reason = None
        if valid_token:
            try:
                # Set the ``enable_two_step_verification`` to True
                two_step_verification_secret = get_or_create_secret(user)
                user.setMemberProperties(
                    mapping = {
                        'enable_two_step_verification': True,
                        'two_step_verification_secret': two_step_verification_secret,
                        'mobile_number_reset_code': '',
                    }
                    )

                IStatusMessage(self.request).addStatusMessage(
                    _("Two-step verification is successfully enabled for your account."),
                    'info'
                    )
                redirect_url = "{0}/@@personal-information".format(self.context.absolute_url())
            except Exception as e:
                reason = _(str(e))
        else:
            reason = _("Invalid token or token expired.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(_("Setup failed! {0}").format(reason), 'error')
            redirect_url = "{0}/@@setup-two-step-verification".format(self.context.absolute_url())

        self.request.response.redirect(redirect_url)

    def updateFields(self, *args, **kwargs):
        """
        Check if user has a mobile number. If not, redirect him to the page to set it up.
        """
        if bool(api.user.is_anonymous()) is False:
            user = api.user.get_current()
            mobile_number = user.getProperty('mobile_number')
            if not mobile_number:
                redirect_url = "{0}/@@setup-mobile-number".format(self.context.absolute_url())
                self.request.response.redirect(redirect_url)

            return super(SetupTwoStepVerificationForm, self).updateFields(*args, **kwargs)

# View for the ``SetupForm``.
SetupTwoStepVerificationFormView = wrap_form(SetupTwoStepVerificationForm)
