from uuid import uuid4

from zope.i18nmessageid import MessageFactory

from collective.smsauthenticator.helpers import get_app_settings
from collective.smsauthenticator.userdataschema import IEnhancedUserDataSchema,\
    UserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchemaProvider
from collective.smsauthenticator.pas_plugin import SMSAuthenticatorPlugin
from zope.component import getUtility, getAllUtilitiesRegisteredFor
from zope.component import ComponentLookupError

from Products.CMFCore.interfaces import ISiteRoot
from zope.interface.interfaces import IInterface
import logging

uninstall_logger = logging.getLogger("collective.smsauthenticator.uninstall")
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
    uninstall_persistent_userdataschemaprovider(context)


def uninstall_persistent_userdataschemaprovider(context):
    """ We  need to get rid off a VERY persistent UserDataSchemaProvider.
    We tried to do this the 'nice' way, via unregisterUtility, and other
    unregister functionality of the SiteMangers, but it just did not work.
    Our UserDataSchemaProvider object kept  popping up after removing the
    product.
    Resulting in fatal errors like these when hitting plone:

    TypeError: ('object.__new__(UserDataSchemaProvider) is not safe,
    use persistent.Persistent.__new__()',
    <function _reconstructor at 0x7ff92a4f4668>,
    (<class 'collective.smsauthenticator.userdataschema.UserDataSchemaProvider'>,
    <type 'object'>, None))

    And of course a nice warning:
    WARNING OFS.Uninstalled Could not import class 'UserDataSchemaProvider'
        from module 'collective.smsauthenticator.userdataschema'

    We do the following:
    1. Get the IUserDataSchemaProvider util
    2. Get the IEnhancedUserDataSchema util (the same as #1, other interface)
    3. Get the BaseComponent sitemanager (zope.component.registry)
    4. Get the PersistentComponents sitemanger (five.localsitemanager.registry)
    5. For each of thse sitemanagers:
        a. Loop over _adapters, delete anything related to our product,
            or userdata
        b. Loop over _subscribers, delete anything related to our product,
            or userdata
        c. Loop over _provided, delete anything related to our product,
            or userdata
    6. Delete the utils from #1. and #2.

    """
    from zope.component.hooks import getSiteManager
    # Get our util
    util = None
    try:
        util = getUtility(IEnhancedUserDataSchema)
    except ComponentLookupError:
        pass

    # Get plone.app.user util
    util2 = None
    try:
        util2 = getUtility(IUserDataSchemaProvider)
    except ComponentLookupError:
        pass

    # Get the sitemanagers involved
    components_sm = getSiteManager()
    base_sm = getSiteManager(context=context)

    # Loop over the sitemanagers
    for sm in [base_sm, components_sm]:
        uninstall_logger.info("Handeling {0}".format(sm))

        # Get the lowlevel registry stuff.
        adapters = sm.utilities._adapters
        subscribers = sm.utilities._subscribers
        provided = sm.utilities._provided

        # Adapter looping
        for x in adapters[0].keys():
            if x.__module__.find("smsauthenticator") != -1\
               or x.__module__.find("userdata") != -1:
                del adapters[0][x]
                uninstall_logger.info("Removed adapter: {0}"
                                      .format(x))
        # Overwrite the adapters
        sm.utilities._adapters = adapters

        # Subscribers looping
        for x in subscribers[0].keys():
            if x.__module__.find("smsauthenticator") != -1\
               or x.__module__.find("userdata") != -1:
                del subscribers[0][x]
                uninstall_logger.info("Removed subscriber: {0}"
                                      .format(x))
        # Overwrite the subscribers
        sm.utilities._subscribers = subscribers

         # Provided looping
        for x in provided.keys():
            if x.__module__.find("smsauthenticator") != -1\
               or x.__module__.find("userdata") != -1:
                del provided[x]
                uninstall_logger.info("Removed provider: {0}"
                                      .format(x))
        # Overwrite the provided
        sm.utilities._provided = provided

    # Ensure this is commited
    import transaction
    transaction.commit()

    # Delete the utils. No idea if needed
    # But this works like this, so keeping it.
    if util:
        del util
    if util2:
        del util2
    uninstall_logger.info("Done ..")
