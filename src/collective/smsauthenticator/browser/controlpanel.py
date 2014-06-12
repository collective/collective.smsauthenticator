import logging

from zope.component import getUtility

from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import TextLine, Bool, Text, Int

from plone.registry.interfaces import IRegistry
from plone import api
from plone.app.registry.browser import controlpanel
from plone.autoform.form import AutoExtensibleForm
from plone.directives.form import fieldset

from z3c.form import form, button

from Products.statusmessages.interfaces import IStatusMessage

from collective.smsauthenticator.browser.helpers import get_app_links

logger = logging.getLogger("collective.smsauthenticator")

_ = MessageFactory('collective.smsauthenticator')


class ISMSAuthenticatorSettings(Interface):
    """
    Global SMS Authenticator settings.
    """
    # Local settings
    globally_enabled = Bool(
        title = _("Globally enabled"),
        description = _("If checked, globally enables the two-step verification for all users; "
                        "otherwise - each user configures it himself. Note, that unchecking the "
                        "checkbox does not disable the two-step verification for all users."),
        required = False,
        default = True,
        )
    ip_addresses_whitelist = Text(
        title = _("White-listed IP addresses"),
        description = _("Two-step verification will be ommit for users that log in from white "
                        "listed addresses."),
        required = False,
        default = u'',
        )

    fieldset(
        'main',
        label=_("Main"),
        fields=['globally_enabled', 'ip_addresses_whitelist',]
        )

    # Twilio settings
    twilio_number = TextLine(
        title = _("Twilio number"),
        description = _("Enter your Twilio (phone) number."),
        required = True,
        default = u'',
        )

    twilio_account_sid = TextLine(
        title = _("Twilio AccountSID"),
        description = _("Enter your Twilio AccountSID."),
        required = True,
        default = u'',
        )

    twilio_auth_token = TextLine(
        title = _("Twilio AuthToken"),
        description = _("Enter your Twilio AuthToken."),
        required = True,
        default = u'',
        )

    fieldset(
        'twilio',
        label=_("Twilio"),
        fields=['twilio_number', 'twilio_account_sid', 'twilio_auth_token',]
        )

    # Security settings
    ska_secret_key = TextLine(
        title = _("Secret Key"),
        description = _("Enter your secret key for the site here. When choosing a secret key, "
                        "think of it as some sort of a password."),
        required = False,
        default = u'',
        )

    ska_token_lifetime = Int(
        title = _("Token lifetime"),
        description = _("Authentication token lifetime in seconds."),
        required = False,
        default = 300, # 15 minutes
        )

    fieldset(
        'security',
        label=_("Security"),
        fields=['ska_secret_key', 'ska_token_lifetime',]
        )


class SMSAuthenticatorSettingsEditForm(AutoExtensibleForm, form.EditForm):
    """
    Control panel form.
    """
    control_panel_view = "plone_control_panel"
    schema_prefix = None
    schema = ISMSAuthenticatorSettings
    label = _("SMS Authenticator")
    description = _(u"""SMS Authenticator configuration""")

    def updateFields(self):
        super(SMSAuthenticatorSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(SMSAuthenticatorSettingsEditForm, self).updateWidgets()

    def getContent(self):
        return getUtility(IRegistry).forInterface(self.schema, prefix=self.schema_prefix)

    def updateActions(self):
        super(SMSAuthenticatorSettingsEditForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    def render(self, *args, **kwargs):
        res = super(SMSAuthenticatorSettingsEditForm, self).render(*args, **kwargs)
        additional_template = self.context.restrictedTraverse('control_panel_extra')
        template_context = get_app_links(self.context)
        template_context.update({'charset': 'utf-8'})
        additional = additional_template(**template_context)
        return res + additional

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        """
        Update properties of all users.
        """
        from collective.smsauthenticator.helpers import (
            enable_two_step_verification_for_users, disable_two_step_verification_for_users
            )
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        globally_enabled = data.get('globally_enabled', None)

        if globally_enabled is True:
            # Enable for all users
            users = api.user.get_users()
            enable_two_step_verification_for_users(users)
            logger.debug('Enabled')
        elif globally_enabled is False:
            # Disable for all users
            users = api.user.get_users()
            #disable_two_step_verification_for_users(users)
            logger.debug('Disabled')

        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))


class SMSAuthenticatorSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    Control panel.
    """
    form = SMSAuthenticatorSettingsEditForm
