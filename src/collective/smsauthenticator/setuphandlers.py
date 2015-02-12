from uuid import uuid4

from zope.i18nmessageid import MessageFactory

from collective.smsauthenticator.helpers import get_app_settings
from collective.smsauthenticator.pas_plugin import SMSAuthenticatorPlugin

_ = MessageFactory('collective.smsauthenticator')

PAS_TITLE = 'SMS Authenticator plugin (collective.smsauthenticator)'
PAS_ID = 'sms_auth'

def _add_plugin(pas, pluginid=PAS_ID):
    """
    Install and activate collective.smsauthenticator PAS plugin
    """
    installed = pas.objectIds()
    if pluginid in installed:
        return PAS_TITLE + " already installed."
    plugin = SMSAuthenticatorPlugin(pluginid, title=PAS_TITLE)
    pas._setObject(pluginid, plugin)
    plugin = pas[plugin.getId()] # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info['interface']
        if not interface.providedBy(plugin):
            continue
        pas.plugins.activatePlugin(interface, plugin.getId())
        pas.plugins.movePluginsDown(
            interface,
            [x[0] for x in pas.plugins.listPlugins(interface)[:-1]],
        )

def _remove_plugin(pas, pluginid=PAS_ID):
    """
    Deactivate and uninstall collective.smsauthenticator PAS plugin
    """
    installed = pas.objectIds()
    if pluginid not in installed:
        return PAS_TITLE + " not installed."
    plugin = SMSAuthenticatorPlugin(pluginid, title=PAS_TITLE)

    plugin = pas[plugin.getId()] # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info['interface']
        if not interface.providedBy(plugin):
            continue
        pas.plugins.deactivatePlugin(interface, plugin.getId())

    pas._delObject(pluginid, plugin)

def _setup_secret_key(portal):
    """
    Generate secret key
    """
    portal.portal_setup.runImportStepFromProfile(
        'profile-collective.smsauthenticator:default',
        'plone.app.registry'
        )

    settings = get_app_settings()
    if not settings.ska_secret_key:
        settings.ska_secret_key = unicode(uuid4())

def setupVarious(context):
    """
    @param context: Products.GenericSetup.context.DirectoryImportContext instance
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other proudct
    if context.readDataFile('collective.smsauthenticator.marker.txt') is None:
        # Not your add-on
        return

    portal = context.getSite()

    _setup_secret_key(portal)

    pas = portal.acl_users
    _add_plugin(pas)

def uninstall(context):
    """
    Remove the PAS plugin.
    """
    if context.readDataFile('collectivesmsauthenticator_uninstall.txt') is None:
        return

    portal = context.getSite()
    pas = portal.acl_users
    _remove_plugin(pas)
