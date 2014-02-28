from Products.CMFCore.utils import getToolByName
import unittest2 as unittest
from plone.testing.z2 import Browser
from plone.app.testing import quickInstallProduct
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD, TEST_USER_NAME, TEST_USER_PASSWORD
from plone import api

from collective.smsauthenticator.testing import \
    COLLECTIVE_SMSAUTHENTICATOR_INTEGRATION_TESTING
from collective.smsauthenticator.tests.base import BaseTest


class TestGeneric(unittest.TestCase, BaseTest):

    layer = COLLECTIVE_SMSAUTHENTICATOR_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.portal_url = api.portal.get().absolute_url()
        self._install()

    def test_(self):
        """
        """
        