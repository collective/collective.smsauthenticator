rm docs/*.rst
rm -rf builddocs/
./bin/sphinx-apidoc src/collective --full -o docs -H 'collective.smsauthenticator' -A 'Goldmund, Wyldebeast & Wunderliebe <info@gw20e.com>' -V '0.1' -f -d 20
cp docs/conf.dist docs/conf.py