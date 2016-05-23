from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PluggableAuthService.interfaces.authservice import IBasicUser
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent
from collective.smsauthenticator.helpers import get_app_settings
from plone import api
from plone.app.users.browser.personalpreferences import UserDataPanel
from plone.app.users.userdataschema import IUserDataSchema, IUserDataSchemaProvider
from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema import Bool, TextLine, Text

import logging


logger = logging.getLogger("collective.smsauthenticator")

_ = MessageFactory('collective.smsauthenticator')

class CustomizedUserDataPanel(UserDataPanel):
    """
    Customise the user form shown in personal-preferences.
    """
    def __init__(self, context, request):
        super(CustomizedUserDataPanel, self).__init__(context, request)

        # Removing certain fields from form
        self.form_fields = self.form_fields.omit(
            'enable_two_step_verification',
            'mobile_number',
            'two_step_verification_secret',
            'mobile_number_reset_token',
            'mobile_number_reset_code',
            'mobile_number_authentication_code',
            'ips',
            # 'authentication_token_valid_until',
            )


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema


def verification_default_enabled():
    """
    Returns the value of `ISMSAuthenticatorSettings.globally_enabled`.
    Used as default value for `IEnhancedUserDataSchema.enable_two_step_verification`.
    """
    settings = get_app_settings()
    return settings.globally_enabled


class IEnhancedUserDataSchema(IUserDataSchema):
    """
    Extended user profile.

    :property bool enable_two_step_verification: Indicates, whether the two-step verification is
                                                     enabled for the user.
    :property string two_step_verification_secret: Secret key of the user (unique per user).
                                                       Automatically generated.
    :property string mobile_number_reset_token: Token to reset users' mobile number. Automatically
                                                generated.
    :property string mobile_number_reset_code: Code to reset users' mobile number (sent by SMS).
                                               Automatically generated.
    :property string mobile_number_authentication_code: Latest code sent by SMS to users' mobile
                                                        number for authentication. Automatically
                                                        generated.
    """
    enable_two_step_verification = Bool(
        title=_('Enable two-step verification.'),
        description=_("""Enable/disable the two-step verification. Click\
                      <a href='@@setup-mobile-number'>here</a> to set it up or\
                      <a href='@@disable-two-step-verification'>here</a> to disable it."""
            ),
        required=False,
        defaultFactory=verification_default_enabled,
        )

    mobile_number = TextLine(
        title=_('Mobile number'),
        description=_("Users' mobile number"),
        required=False,
    )

    two_step_verification_secret = TextLine(
        title=_('Secret key'),
        description=_('Automatically generated'),
        required=False,
    )

    mobile_number_reset_token = TextLine(
        title=_('Token to reset the mobile number'),
        description=_('Automatically generated'),
        required=False,
    )

    mobile_number_reset_code = TextLine(
        title=_('Code to reset the mobile number (sent by SMS)'),
        description=_('Automatically generated'),
        required=False,
    )

    mobile_number_authentication_code = TextLine(
        title=_('Last authentication code'),
        description=_('Automatically generated each time SMS message is sent'),
        required=False,
    )

    ips = Text(
        title=_('List of IPs user logged from'),
        description=_('Automatically generated each time user logs in'),
        required=False,
    )

    # authentication_token_valid_until = TextLine(
    #    title = _('Last token valid until'),
    #    description = _('Automatically generated each time SMS message is sent'),
    #    required = False,
    # )


@adapter(IBasicUser, IPrincipalCreatedEvent)
def userCreatedHandler(principal, event):
    """
    Fired upon creation of each user. If app setting ``globally_enabled`` is set to True,
    two-step verification would be automatically enabled for the registered users (in that
    case they would have to go through the mobile number recovery procedure.

    The ``principal`` value is seems to be a user object, although it does not have
    the ``setMemberProperties`` method defined (that's why we obtain the user
    using `plone.api`, 'cause that one has it).
    """
    from collective.smsauthenticator.helpers import (
        is_two_step_verification_globally_enabled, get_or_create_secret
        )
    # This function is also triggered for Zope Users
    # We don't need to execute this code for them
    # Zope users are "PropertiedUser", while Plone users are "PloneUser"
    if hasattr(principal, "__class__") and PloneUser != principal.__class__:
        logger.debug("Zope User detetected, ignoring")
        return

    user = api.user.get(username=principal.getId())
    if is_two_step_verification_globally_enabled():
        get_or_create_secret(user)
        user.setMemberProperties(mapping={'enable_two_step_verification': True})

    logger.debug(user.getProperty('enable_two_step_verification'))
    logger.debug(user.getProperty('two_step_verification_secret'))
