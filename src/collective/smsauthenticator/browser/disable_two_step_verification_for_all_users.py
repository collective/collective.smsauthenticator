from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from collective.smsauthenticator.helpers import disable_two_step_verification_for_users

_ = MessageFactory('collective.smsauthenticator')

class DisableTwoStepVerificationForAllUsers(BrowserView):
    """
    Disable the two-step verification for all users.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def index(self):
        """
        Disble the two-step verification for the user and redirect back to the `@@sms-authenticator-settings`.
        """
        users = api.user.get_users()
        disable_two_step_verification_for_users(users)

        IStatusMessage(self.request).addStatusMessage(
            _("You have successfully disabled the two-step verification for all users."),
            'info'
            )
        redirect_url = "{0}/@@sms-authenticator-settings".format(self.context.absolute_url())
        self.request.response.redirect(redirect_url)
