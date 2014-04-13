# coding: utf-8
import os


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


def to_unicode(value):
    if isinstance(value, unicode):
        return value
    if isinstance(value, basestring):
        return value.decode('utf-8')
    if isinstance(value, int):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value


def to_str(value):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    if isinstance(value, int):
        return str(value)
    return value


def parse_config_file(app, filename):
    if not filename or not os.path.exists(filename):
        app.logger.warning('Configuration file %s does not exist.' % filename)
        return
    if filename.endswith('.py'):
        try:
            app.config.from_pyfile(filename)
        except IOError:
            app.logger.warning("Cannot load configuration "
                               "from python file %s" % filename)
    else:
        app.config.from_object(filename)
