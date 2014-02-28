from Products.CMFCore.utils import getToolByName
import unittest2 as unittest
from plone.testing.z2 import Browser
from plone import api
from plone.app.testing import quickInstallProduct
from collective.smsauthenticator.setuphandlers import PAS_ID

from collective.smsauthenticator.testing import \
    COLLECTIVE_SMSAUTHENTICATOR_INTEGRATION_TESTING
from collective.smsauthenticator.tests.base import BaseTest


class TestPas(unittest.TestCase, BaseTest):

    layer = COLLECTIVE_SMSAUTHENTICATOR_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.pas = getToolByName(self.portal, 'acl_users')
        self.portal_url = api.portal.get().absolute_url()
        self._install()

    def test_plugin_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        installed = self.pas.objectIds()
        self.assertIn(PAS_ID, installed)
