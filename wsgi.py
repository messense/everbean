#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass

import logging
from everbean.app import create_app

app = create_app()

if app.config['SENTRY_DSN']:
    from raven.contrib.flask import Sentry
    Sentry(app, logging=True, level=logging.ERROR)
