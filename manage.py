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

import time
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.assets import ManageAssets
from everbean import tasks
from everbean.app import create_app
from everbean.core import db
from everbean.models import User

app = create_app()

manager = Manager(app)

manager.add_option('-c', '--config', dest='config', required=False)
manager.add_option('-e', '--envvar', dest='envvar', required=False)

migrate = Migrate(app, db)

manager.add_command("db", MigrateCommand)
manager.add_command("assets", ManageAssets())


def run_dev(profile_log=None):
    """Runs a development server."""
    app.debug = True

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
def syncdb():
    try:
        db.create_all()
        print('Database creation succeed.')
    except:
        print('Database creation failed.')


@manager.command
def livereload():
    from livereload import Server
    app.debug = True
    server = Server(app)
    server.watch("everbean/*.py")
    server.watch("everbean/templates/*.html")
    server.watch("everbean/static/css/*.css")
    server.watch("everbean/static/js/*.js")
    server.serve(port=app.config['PORT'])


@manager.command
def cronjob():
    # refresh access token one day before access token expires
    refresh_access_token()
    sync_books()
    sync_notes()


def refresh_access_token():
    expires_time = int(time.time()) - 86400
    users = User.query.filter_by(enable_sync=True, douban_expires_at__lte=expires_time).all()
    for user in users:
        tasks.refresh_douban_access_token.delay(user)


def sync_books():
    users = User.query.filter_by(enable_sync=True).all()
    for user in users:
        tasks.sync_books.delay(user)


def sync_notes():
    users = User.query.filter(User.enable_sync == True, User.evernote_access_token != None).all()
    for user in users:
        tasks.sync_notes(user)


if __name__ == '__main__':
    manager.run()
