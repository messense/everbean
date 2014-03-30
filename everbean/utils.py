# coding: utf-8
import os
import sys
from evernote.api.client import EvernoteClient
from douban_client.client import DoubanClient


def parse_command_line(app, args=None, final=True):
    if args is None:
        args = sys.argv
    config = dict()
    for i in range(1, len(args)):
        # All things after the last option are command line arguments
        if not args[i].startswith("-"):
            break
        if args[i] == "--":
            break
        arg = args[i].lstrip("-")
        name, equals, value = arg.partition("=")
        name = name.replace('-', '_').upper()
        if not name in app.config:
            app.logger.warning('Unrecognized command line option: %r' % name)
        # convert to bool
        if value == 'True':
            value = True
        if value == 'False':
            value = False
        config[name] = value
        if final:
            app.config[name] = value

    return config


def parse_config_file(app, filename):
    if not os.path.exists(filename):
        app.logger.warning('Configuration file %s does not exist.' % filename)
        return
    if filename.endswith('.py'):
        try:
            app.config.from_pyfile(filename)
        except IOError:
            app.logger.warning("Cannot load configuration from python file %s" % filename)
    else:
        app.config.from_object(filename)


def get_evernote_client(app, is_i18n=True, token=None):

    def get_evernote_service_host():
        if app.config['EVERNOTE_SANDBOX']:
            return 'sandbox.evernote.com'
        if is_i18n:
            return 'wwww.evernote.com'
        else:
            return 'app.yinxiang.com'

    if token:
        client = EvernoteClient(token=token,
                                sandbox=app.config['EVERNOTE_SANDBOX'],
                                service_host=get_evernote_service_host())
    else:
        client = EvernoteClient(consumer_key=app.config['EVERNOTE_CONSUMER_KEY'],
                                consumer_secret=app.config['EVERNOTE_CONSUMER_SECRET'],
                                sandbox=app.config['EVERNOTE_SANDBOX'],
                                service_host=get_evernote_service_host())

    return client


def get_douban_client(app, token=None):
    client = DoubanClient(app.config['DOUBAN_API_KEY'],
                          app.config['DOUBAN_API_SECRET'],
                          app.config['DOUBAN_REDIRECT_URI'],
                          app.config['DOUBAN_API_SCOPE'])
    if token:
        client.auth_with_token(token)
    return client
