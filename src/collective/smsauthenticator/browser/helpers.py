from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.smsauthenticator')

def get_app_links(context):
    """
    Gets SMS authenticator app links.
    """
    return {
        # Settings URL
        'settings_url': '{0}/{1}'.format(context.absolute_url(), '@@sms-authenticator-settings'),
        'settings_text': _("SMS Authenticator configuration"),
        # Enable URL
        'enable_url': '{0}/{1}'.format(context.absolute_url(), '@@sms-authenticator-enable-for-all-users'),
        'enable_text': _("Enable two-step verification for all users"),
        # Disable URL
        'disable_url': '{0}/{1}'.format(context.absolute_url(), '@@sms-authenticator-disable-for-all-users'),
        'disable_text':  _("Disable two-step verification for all users"),
        # See all IPs URL
        'show_all_user_ips_url': '{0}/{1}'.format(context.absolute_url(), '@@sms-authenticator-show-all-user-ips'),
        'show_all_user_ips_text': _("Show all user IPs"),
        # See unique IPs URL
        'show_unique_user_ips_url': '{0}/{1}'.format(context.absolute_url(), '@@sms-authenticator-show-unique-user-ips'),
        'show_unique_user_ips_text': _("Show unique user IPs"),
    }
