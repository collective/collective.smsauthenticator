__title__ = 'collective.smsauthenticator'
__version__ = '0.3.1'
__build__ = 0x00000d
__author__ = 'Goldmund, Wyldebeast & Wunderliebe <info@gw20e.com>'
__copyright__ = 'Goldmund, Wyldebeast & Wunderliebe'
__license__ = 'GPL 2.0/LGPL 2.1'

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
