from plone.testing.z2 import Browser
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

class BaseTest(object):

    def _install(self):

        browser = Browser(self.app)

        # Login as site owner
        browser.open('{0}/login_form'.format(self.portal.absolute_url()))
        browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
        browser.getControl(name='submit').click()

        # We must uninstall and install the package, it seems generic setup profile
        # is not applied coorectly by plone.app.testing in this testing layer.
        browser.open('{0}/prefs_install_products_form'.format(self.portal.absolute_url()))

        form = browser.getForm(index=1)
        self.assertEqual(
            form.action, '{0}/portal_quickinstaller/installProducts'.format(self.portal.absolute_url()),
            u'Install form not found')
        products_list = form.getControl(name='products:list')
        if "collective.smsauthenticator" in products_list.options:
            products_list.value = (u"collective.smsauthenticator",)
            form.getControl(label='Activate').click()
        browser.open(self.portal.absolute_url() + '/logout')

    def _get_browser(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        return browser

    def _login_browser(self, browser, user, passwd):
        browser.open(self.portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = user
        browser.getControl(name='__ac_password').value = passwd
        browser.getControl(name='submit').click()