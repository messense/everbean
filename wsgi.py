#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

_has_gevent = True
try:
    import gevent
except ImportError:
    _has_gevent = False
if _has_gevent:
    from gevent import monkey
    # apply gevent monkey patch
    monkey.patch_all()

import sys
from everbean.app import create_app


def run_server():
    """Runs a deployment server"""
    app = create_app()
    port = int(app.config['PORT'])
    if app.debug:
        print('Start server at: 127.0.0.1:%s in debug mode.' % port)
    else:
        print('Start server at: 127.0.0.1:%s' % port)

    def _run_server():
        from gevent.wsgi import WSGIServer
        http_server = WSGIServer(('', port), app)
        try:
            http_server.serve_forever()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting application...')
            sys.exit(0)

    def _run_simple():
        from werkzeug.serving import run_simple
        try:
            run_simple('0.0.0.0', port, app, use_reloader=app.debug, use_debugger=app.debug)
        except (EOFError, KeyboardInterrupt):
            print('\nExiting application...')
            sys.exit(0)

    if _has_gevent:
        _run_server()
    else:
        _run_simple()

if __name__ == '__main__':
    run_server()
