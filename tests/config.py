# configuration file

# douban api key
DOUBAN_API_KEY = 'test'
# douban api secret
DOUBAN_API_SECRET = 'test'
# douban api scope
DOUBAN_API_SCOPE = 'douban_basic_common,book_basic_r,book_basic_w'
# douban redirect uri
DOUBAN_REDIRECT_URI = 'test'

# evernote consumer key
EVERNOTE_CONSUMER_KEY = 'test'
# evernote consumer secret
EVERNOTE_CONSUMER_SECRET = 'test'
# evernote redirect uri
EVERNOTE_REDIRECT_URI = 'test'
# is running in sandbox?
EVERNOTE_SANDBOX = True
# evernote sandbox token
EVERNOTE_SANDBOX_TOKEN = ''

# is debugging
DEBUG = True
# server listen port
PORT = 5000
# session secret key
SECRET_KEY = 'everbean-dev'

# MySQL database URI
SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/everbean'

# Cache type
CACHE_TYPE = "memcached"
# Cache key prefix
CACHE_KEY_PREFIX = "everbean_"

# Celery broker url
BROKER_URL = 'amqp://guest@localhost//'

# mail server
MAIL_SERVER = ''
# mail port
MAIL_PORT = 25
# mail username
MAIL_USERNAME = ''
# mail password
MAIL_PASSWORD = ''
