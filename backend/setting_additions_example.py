# coding: utf-8
# Copy this file and rename to 'setting_additions.py' at
# the same directory, apply own values - this is required to run site

# The following settings must be changed for each project individually
# This file is add to .gitignore, so you will have no problems on update

SOCIAL_AUTH_VK_OAUTH2_KEY = '1111'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'abcd'
SERVICE_KEY_VK = 'abcd'
QUESTION_DEFAULT_APPROVED = False
REGISTRATION_TOKEN = ''
#DEBUG = False
DEBUG = True
SECRET_KEY = 'abcd'

IS_EMERGENCY_LOGIN_MODE = False
#IS_EMERGENCY_LOGIN_MODE = True
IS_ID_RECOGNITION_BROKEN_VK = False
#IS_ID_RECOGNITION_BROKEN_VK = True

#IS_AGRESSIVE_QUESTION_NOTIFICATION = False
IS_AGRESSIVE_QUESTION_NOTIFICATION = True

PAYMENT_TEXT_YANDEX = 'Testing...'
PAYMENT_YANDEX_ENABLE_CARD = True
PAYMENT_YANDEX_ENABLE_PHONE = False
PAYMENT_SUCCESS_REDIRECT_YANDEX = 'http://localhost/services/'
PAYMENT_SECRET_YANDEX = 'abcd'
PAYMENT_ACCOUNT_YANDEX = '1111'

WEBMASTER_TAG_YANDEX = '<meta name="yandex-verification" content="111" />'
WEBMASTER_TAG_GOOGLE = '<meta name="google-site-verification" content="111" />'

# OPTIONAL

SITE_TAB_NAME = 'Student council'
