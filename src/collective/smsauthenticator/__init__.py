# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory

from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from collective.smsauthenticator.pas_plugin import (
    SMSAuthenticatorPlugin, addSMSAuthenticatorPlugin, manage_addSMSAuthenticatorPluginForm
    )

_ = MessageFactory('collective.smsauthenticator')

def initialize(context):
    """
    Initializer called when used as a Zope 2 product.
    """
    registerMultiPlugin(SMSAuthenticatorPlugin.meta_type) # Add to PAS menu
    context.registerClass(
        SMSAuthenticatorPlugin,
        constructors = (manage_addSMSAuthenticatorPluginForm, addSMSAuthenticatorPlugin),
        visibility = None
        )
