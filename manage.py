#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.assets import ManageAssets
from everbean.app import create_app
from everbean.core import db

app = create_app()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("db", MigrateCommand)
manager.add_command("assets", ManageAssets())

def run_dev(profile_log=None):
    """Runs a development server."""
    from werkzeug.serving import run_simple
    from werkzeug.debug import DebuggedApplication
    from werkzeug.contrib.profiler import ProfilerMiddleware

    port = int(app.config['PORT'])

    if profile_log:
        f = open(profile_log, 'w')
        wsgi = ProfilerMiddleware(app, f)
    else:
        wsgi = DebuggedApplication(app)

    run_simple('0.0.0.0', port, wsgi, use_reloader=True, use_debugger=True)


@manager.command
def run():
    run_dev()

@manager.command
def profile():
    log = '/tmp/everbean-profile.log'
    run_dev(log)

@manager.command
def create_db():
    from everbean.models import User, Book
    try:
        db.create_all()
        print('Database creation succeed.')
    except:
        print('Database creation failed.')


if __name__ == '__main__':
    manager.run()
