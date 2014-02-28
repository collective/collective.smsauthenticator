from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

_ = MessageFactory('collective.smsauthenticator')

class DisableTwoStepVerification(BrowserView):
    """
    Disabling the two-step verification.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def disable(self):
        """
        Disable the two-step verification for the user and redirect back to the `@@personal-information`.
        """
        if bool(api.user.is_anonymous()) is True:
            self.request.response.setStatus(401, _('Forbidden for anonymous'), True)
            return None

        user = api.user.get_current()
        user.setMemberProperties(
            mapping = {
                'enable_two_step_verification': False,
                'two_step_verification_secret': '',
                'mobile_number_reset_token': '',
                'mobile_number_reset_code': '',
                #'authentication_token_valid_until': '',
                'mobile_number_authentication_code': '',
            }
            )

        IStatusMessage(self.request).addStatusMessage(
            _("You have successfully disabled the two-step verification for your account."),
            'info'
            )
        # TODO: redirect user to where he actually came from?
        redirect_url = "{0}/@@personal-information".format(self.context.absolute_url())
        self.request.response.redirect(redirect_url)
