from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectivesmsauthenticatorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.smsauthenticator
        xmlconfig.file(
            'configure.zcml',
            collective.smsauthenticator,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'collective.smsauthenticator')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'collective.smsauthenticator')


COLLECTIVE_SMSAUTHENTICATOR_FIXTURE = CollectivesmsauthenticatorLayer()
COLLECTIVE_SMSAUTHENTICATOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_SMSAUTHENTICATOR_FIXTURE,),
    name="CollectivesmsauthenticatorLayer:Integration"
)
COLLECTIVE_SMSAUTHENTICATOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_SMSAUTHENTICATOR_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivesmsauthenticatorLayer:Functional"
)
