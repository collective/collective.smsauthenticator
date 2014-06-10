from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView

_ = MessageFactory('collective.smsauthenticator')

class ListUserIPs(BrowserView):
    """
    List user IPS.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_user_unique_ips(self, user):
        """
        """
        unique_ips = set()
        raw_ips = user.getProperty('ips')

        if raw_ips:
            all_ips = raw_ips.split('\n')

            for ip_line in all_ips:
                ip, visit = ip_line.split(',', 2)
                unique_ips.append(ip)

        return unique_ips

    def unique(self):
        """
        List unique user IPs.
        """
        users = api.user.get_users()
        ips = set()
        for user in users:
            ips.update(self._get_user_unique_ips(user))
        return ips

    def all(self):
        """
        List all user IPs.
        """
        return 'all'

