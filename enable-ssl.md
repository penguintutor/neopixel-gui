[Based on certbot from https://certbot.eff.org/#pip-other]

wget https://dl.eff.org/certbot-auto
chmod a+x certbot-auto
./certbot-auto certonly 
(follow the prompts)

How would you like to authenticate with the ACME CA?
-------------------------------------------------------------------------------
1: Spin up a temporary webserver (standalone)
2: Place files in webroot directory (webroot)
-------------------------------------------------------------------------------

Choose 1

Agree to terms and conditions

Please enter in your domain name(s) (comma and/or space separated)

Select the webroot for home.penguintutor.com:
-------------------------------------------------------------------------------
1: Enter a new webroot
-------------------------------------------------------------------------------

It saves cert in 
/etc/letsencrypt/live/<domain name>/fullchain.pem
and key in
/etc/letsencrypt/live/<domain name>/privkey.pem

This needs to be combined eg.
sudo -s
cd /etc/letsencrypt/live/<domain name>/
cat fullchain.pem privkey.pem > combined.pem

