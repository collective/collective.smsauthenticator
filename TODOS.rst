TODOs/Roadmap
================================================
Based on the MoSCoW principle. Must haves and should haves are planned to be worked on.

* Features/issues marked with plus (+) are implemented/solved.
* Features/issues marked with minus (-) are yet to be implemented.

Must haves
------------------------------------------------
+ At the moment, Plone top login link (AJAX overlay) doesn't work with SMS Authenticator. Default
  "popupforms.js" has been overridden by a custom one, where the part of login forms being shown in
  an overlay has been commented out. Make SMS Authenticator working with overlays.
+ Keep a log of users and IPs they have came from, so that admins could add these IP addresses to
  the white list.
+ Add nice templates for user IPs helper views.
- Possibly to be able to set the SMSAuthenticator required for certain users/groups
  to use the two-step verification.
- When SMSAuthenticator is skipped (white-listed address or user that doesn't have it enabled),
  the came_from functionality doesn't work.
- On disable two-step verification, redirect user to where he was.
- Get rid of annoying "Sure to leave this page" message when editing the SMSAuthenticator settings.

Should haves
------------------------------------------------
- At the moment SMS Authenticator relies on the API of "Twilio" SMS service provider. Make it possible
  to switch between SMS service providers (or make installable micro apps).

Could haves
------------------------------------------------

Would haves
------------------------------------------------
