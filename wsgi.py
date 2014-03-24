#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

from gevent import monkey
# apply gevent monkey patch
monkey.patch_all()

import sys
from gevent.wsgi import WSGIServer
from everbean.app import create_app

def run_server():
    """Runs a deployment server"""
    app = create_app()
    port = int(app.config['PORT'])
    if app.debug:
        print('Start server at: 127.0.0.1:%s in debug mode.' % port)
    else:
        print('Start server at: 127.0.0.1:%s' % port)

    http_server = WSGIServer(('', port), app)
    try:
        http_server.serve_forever()
    except (EOFError, KeyboardInterrupt):
        print('\nExiting application...')
        sys.exit(0)

if __name__ == '__main__':
    run_server()
