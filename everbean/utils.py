# coding: utf-8
from __future__ import unicode_literals
import os
import six


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


def to_text(s, encoding='utf-8', errors='strict'):
    if isinstance(s, six.text_type):
        return s
    if isinstance(s, six.string_types):
        return six.text_type(s, encoding, errors)
    else:
        if six.PY3:
            if isinstance(s, bytes):
                return six.text_type(s, encoding, errors)
            else:
                return six.text_type(s)
        elif hasattr(s, '__unicode__'):
            return six.text_type(s)
        else:
            return six.text_type(bytes(s), encoding, errors)


def to_bytes(s, encoding='utf-8', errors='strict'):
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if isinstance(s, six.string_types):
        return s.encode(encoding, errors)
    else:
        if six.PY3:
            return six.text_type(s).encode(encoding)
        else:
            return bytes(s)


def parse_config_file(app, filename):
    if not filename or not os.path.exists(filename):
        app.logger.warning('Configuration file %s does not exist.' % filename)
        return
    if filename.endswith('.py'):
        try:
            app.config.from_pyfile(filename)
        except IOError:
            app.logger.warning('Cannot load configuration '
                               'from python file %s' % filename)
    else:
        app.config.from_object(filename)
