The **AVM FRITZ!Box SMS** integration allows you to send SMS via an AVM FRITZ!Box with a cellular modem.

This integration uses a local API which is available with 4G/LTE models of AVM FRITZ!Box.

## Requirements

- AVM FRITZ!Box with internal or USB cellular modem and SMS enabled SIM card.
- User account with app-based second-factor enabled and TOTP secret available.

## Setup on FRITZ!Box

You will want to create a dedicated account for SMS handling purposes as each account can only have
one second-factor attached to it. You will need the second-factor plaintext secret for this account.

1. Login to your FRITZ!Box.
2. Go to System section.
3. Go to FRITZ!Box-User management.
4. Create a new account called for example "fritzsms" and choose a secret password.
5. The user account will need permission to access FRITZ!Box-Settings, but nothing else.
6. After creation, edit the user account again to add TOTP app-based second-factor confirmation.
7. Set "Home Assistant" as Smartphone-Name and reveal the plaintext secret code at the bottom.
8. Remember the username, password and plaintext secret code for the setup in Home Assistant.
9. Proceed with Setup in Home Assistant before finishing second-factor setup.
10. Finish second-factor setup by using the generated TOTP code from step 5. below.

## Setup in Home Assistant

You will want to use [HACS](https://www.hacs.xyz/) to install this custom integration.

1. Login to your Home Assistant.
2. Install custom HACS repository: `https://github.com/mback2k/hafritzsms`
3. Setup new integration "AVM FRITZ!Box SMS" via device settings.
4. Fill in hostname, username, password and second-factor secret for your FRITZ!Box.
5. After confirmation you will get an error, but there is now a generated TOTP to copy into step 10. above.
6. Finish setup on your FRITZ!Box and then confirm the setup in Home Assistant a second time.
7. Click on the 3 dots next to your freshly configured integration to add notification targets.
8. Create a notification target for each mobile number that you want to notify via SMS.
9. The integration will create a notify entity per subconfig entry notification target.
10. You can use the notify entities with the action `notify.send_message` in your automations.
