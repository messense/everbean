#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

from gevent import monkey
# apply gevent monkey patch
monkey.patch_all()

from gevent.wsgi import WSGIServer
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from everbean.app import create_app
from everbean.core import db

app = create_app()

manager = Manager(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

def run_dev(profile_log=None):
    """Runs a development server."""
    from werkzeug.serving import run_with_reloader
    from werkzeug.debug import DebuggedApplication
    from werkzeug.contrib.profiler import ProfilerMiddleware

    port = int(app.config['PORT'])

    if profile_log:
        f = open(profile_log, 'w')
        wsgi = ProfilerMiddleware(app, f)
    else:
        wsgi = DebuggedApplication(app)

    @run_with_reloader
    def _run_server():
        print('Start server at: 127.0.0.1:%s' % port)

        http_server = WSGIServer(('', port), wsgi)
        http_server.serve_forever()

    _run_server()


@manager.command
def run():
    run_dev()

@manager.command
def profile():
    log = '/tmp/everbean-profile.log'
    run_dev(log)

if __name__ == '__main__':
    try:
        manager.run()
    except:
        pass
