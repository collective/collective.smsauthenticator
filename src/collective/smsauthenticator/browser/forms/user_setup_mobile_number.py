"""
User mobile number setup. Here user himself sets the two-step verification.
"""

import logging

from zope.i18nmessageid import MessageFactory

from z3c.form import button, field

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage
from zope.schema import TextLine

from collective.smsauthenticator.helpers import generate_code, send_mobile_number_setup_confirmation_code_sms

logger = logging.getLogger('collective.smsauthenticator')

_ = MessageFactory('collective.smsauthenticator')


class ISetupMobileNumberForm(form.Schema):
    """
    Interface for the SMS Authenticator mobile number setup form.
    """
    mobile_number = TextLine(
        title=_(u"Mobile number"),
        description=_(u"Enter your mobile number to be used for two-step verification."),
        required=True
    )


class SetupMobileNumberForm(form.SchemaForm):
    """
    Form for the SMS Authenticator setup.
    """
    fields = field.Fields(ISetupMobileNumberForm)
    ignoreContext = True
    schema = ISetupMobileNumberForm
    label = _("Setup mobile number for two-step verification")
    description = _(u"To setup two-step verification you need to enter your mobile phone number"
                    u"to which you will be receiving SMS messages with login codes.")
    css_class = "enableAutoFocus"

    @button.buttonAndHandler(_('Verify'))
    def handleSubmit(self, action):
        if bool(api.user.is_anonymous()) is True:
            self.request.response.setStatus(401, _('Forbidden for anonymous'), True)
            return False

        data, errors = self.extractData()
        if errors:
            return False

        mobile_number = data.get('mobile_number', '')
        reason = None

        if mobile_number:
            try:
                # Set the ``enable_two_step_verification`` to True
                user = api.user.get_current()

                # Send a code to confirm the mobile number
                mobile_number_confirmation_code = generate_code(user)

                # Send the SMS
                send_mobile_number_setup_confirmation_code_sms(
                    mobile_number = mobile_number,
                    code = mobile_number_confirmation_code
                    )

                user.setMemberProperties(
                    mapping = {
                        'mobile_number': mobile_number,
                        'mobile_number_reset_code': mobile_number_confirmation_code,
                    }
                    )

                IStatusMessage(self.request).addStatusMessage(
                    _("A confirmation SMS message has been sent to the mobile number specified."),
                    'info'
                    )
                redirect_url = "{0}/@@setup-two-step-verification".format(self.context.absolute_url())
            except Exception as e:
                reason = _(str(e))
        else:
            reason = _("Invalid mobile number.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(_("Setup failed! {0}".format(reason)), 'error')
            redirect_url = "{0}/@@setup-mobile-number".format(self.context.absolute_url())

        self.request.response.redirect(redirect_url)

    def updateFields(self, *args, **kwargs):
        """
        Bar code image is applied here.
        """
        if bool(api.user.is_anonymous()) is False:

            # Something happens here...

            return super(SetupMobileNumberForm, self).updateFields(*args, **kwargs)


# View for the ``SetupMobileNumberForm``.
SetupMobileNumberFormView = wrap_form(SetupMobileNumberForm)
