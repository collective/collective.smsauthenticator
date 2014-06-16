import datetime

from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView

from collective.smsauthenticator.browser.helpers import get_app_links

_ = MessageFactory('collective.smsauthenticator')

class ListUserIPs(BrowserView):
    """
    List user IPS, generic view
    """

    def _get_user_unique_ips(self, user, with_username=False):
        """
        Gets unique IPs of a user.

        :param Products.PlonePAS.tools.memberdata user:
        :return: Set of user unique IPs.
        """
        unique_ips = set()
        raw_ips = user.getProperty('ips', '')

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
                        if with_username:
                            data = (ip, user.getId())
                        else:
                            data = ip
                        unique_ips.add(ip)
                    except Exception as e:
                        pass

        return unique_ips

    def _get_user_ips(self, user, with_username=False):
        """
        Gets all IPs of a user.

        :param Products.PlonePAS.tools.memberdata user:
        :return: List of user IPs.
        """
        unique_ips = []
        raw_ips = user.getProperty('ips', '')

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
                        if with_username:
                            data = (ip, visit, user.getId())
                        else:
                            data = (ip, visit)
                        unique_ips.append(data)
                    except Exception as e:
                        pass

        return unique_ips

    def get_app_links(self):
        """ View function to pass function along to actual helper """
        return get_app_links(self.context)

class ListUniqueUserIPs(ListUserIPs):
    """
    BrowserView for List unique user IPs.
    """

    def get_unique_ips(self):
        users = api.user.get_users()
        ips = set()
        for user in users:
            ips.update(self._get_user_unique_ips(user, with_username=False))

        return ips

class ListAllUserIPs(ListUserIPs):
    """
    BrowserView for List all user IPs.
    """

    def get_all_ips(self):

        users = api.user.get_users()
        ips = []
        for user in users:
            ips += self._get_user_ips(user, with_username=True)

        return ips
