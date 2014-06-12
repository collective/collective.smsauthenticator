import datetime

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
        Gets unique IPs of a user.

        :param Products.PlonePAS.tools.memberdata user:
        :return: Set of user unique IPs.
        """
        unique_ips = set()
        raw_ips = user.getProperty('ips')

        if raw_ips:
            all_ips = raw_ips.split('\n')

            for ip_line in all_ips:
                if ip_line:
                    try:
                        ip, visit = ip_line.split(',', 2)
                        unique_ips.add(ip)
                    except Exception as e:
                        pass

        return unique_ips

    def _get_user_ips(self, user):
        """
        Gets all IPs of a user.

        :param Products.PlonePAS.tools.memberdata user:
        :return: List of user IPs.
        """
        unique_ips = []
        raw_ips = user.getProperty('ips')

        if raw_ips:
            all_ips = raw_ips.split('\n')

            for ip_line in all_ips:
                if ip_line:
                    try:
                        ip, visit = ip_line.split(',', 2)
                        try:
                            visit = datetime.datetime.fromtimestamp(float(visit))
                        except Exception as e:
                            pass
                        unique_ips.append((ip, visit))
                    except Exception as e:
                        pass

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
        users = api.user.get_users()
        ips = []
        for user in users:
            ips += self._get_user_ips(user)
        return ips
