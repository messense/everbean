# coding=utf-8
from __future__ import unicode_literals
# configuration file

SITE_URL = ''

# douban api key
DOUBAN_API_KEY = ''
# douban api secret
DOUBAN_API_SECRET = ''
# douban api scope
DOUBAN_API_SCOPE = 'douban_basic_common,book_basic_r,book_basic_w'
# douban redirect uri
DOUBAN_REDIRECT_URI = ''

# evernote consumer key
EVERNOTE_CONSUMER_KEY = ''
# evernote consumer secret
EVERNOTE_CONSUMER_SECRET = ''
# evernote redirect uri
EVERNOTE_REDIRECT_URI = ''
# is running in sandbox?
EVERNOTE_SANDBOX = True
# evernote sandbox token
EVERNOTE_SANDBOX_TOKEN = ''
# evernote default notebook name
EVERNOTE_NOTEBOOK_NAME = 'Everbean'


# is debugging
DEBUG = False
# server listen port
PORT = 5000
# session secret key
SECRET_KEY = ''

# MySQL database URI
SQLALCHEMY_DATABASE_URI = ''

# Server side session
USE_SERVER_SIDE_SESSION = False
# Server side session type
SESSION_TYPE = 'redis'
# Session key prefix
SESSION_KEY_PREFIX = 'everbean:'

# Cache type
CACHE_TYPE = 'simple'
# Cache key prefix
CACHE_KEY_PREFIX = 'everbean_'

# Celery broker url
BROKER_URL = ''
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

# mail server
MAIL_SERVER = ''
# mail port
MAIL_PORT = 25
# mail username
MAIL_USERNAME = ''
# mail password
MAIL_PASSWORD = ''

# Sentry
SENTRY_DSN = ''
