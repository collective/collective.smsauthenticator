from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView

from collective.smsauthenticator.helpers import (
    is_two_step_verification_globally_enabled, has_enabled_two_step_verification
    )

_ = MessageFactory('collective.smsauthenticator')

class SettingsHelper(BrowserView):
    """
    Helper view for accessing some conditions from portal actions (actions.xml).
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_two_step_verification_globally_enabled(self):
        """
        Disable the two-step verification for the user and redirect back to the `@@personal-information`.
        """
        return is_two_step_verification_globally_enabled()

    def show_enable_two_step_verification_link(self):
        """
        Indicates whether the enable two-step verification link should be shown.

        The following conditions shall be met for True to be returned:

        - User hasn't enabled the two-step verification for his account.
        - In app settings, the globally enable two-step verification is set to False.

        :return bool:
        """
        user = api.user.get_current()
        return not is_two_step_verification_globally_enabled() \
               and (has_enabled_two_step_verification(user) is False)

    def show_disable_two_step_verification_link(self):
        """
        Indicates whether the disable two-step verification link should be shown.

        The following conditions shall be met for True to be returned:

        - User hasn enabled the two-step verification for his account.
        - In app settings, the globally enable two-step verification is set to False.

        :return bool:
        """
        user = api.user.get_current()
        return not is_two_step_verification_globally_enabled() and has_enabled_two_step_verification(user)
