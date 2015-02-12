from Products.CMFCore.utils import getToolByName

from collective.smsauthenticator import __title__

INSTALL = 'profile-%s:default' % __title__
UNINSTALL = 'profile-%s:uninstall' % __title__


def uninstall(portal, reinstall=False):
    """ Uninstall this product.
        This external method is need, because portal_quickinstaller doens't
        know what GenericProfile profile to apply when uninstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(UNINSTALL)
        return "Ran all uninstall steps."
