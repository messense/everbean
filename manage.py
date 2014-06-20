#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function, unicode_literals, with_statement
import time
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.assets import ManageAssets
from flask.ext.failsafe import failsafe
from everbean import tasks
from everbean.core import db
from everbean.models import User


@failsafe
def create_app_for_manager():
    from everbean.app import create_app
    return create_app()

app = create_app_for_manager()
manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command('assets', ManageAssets())


def run_dev(profile_log=None):
    """Runs a development server."""
    from werkzeug.serving import run_simple
    from werkzeug.debug import DebuggedApplication
    from werkzeug.contrib.profiler import ProfilerMiddleware

    app.debug = True
    # print real sql when debugging
    app.config['SQLALCHEMY_ECHO'] = True
    port = int(app.config['PORT'])

    if profile_log:
        f = open(profile_log, 'w')
        wsgi = ProfilerMiddleware(app, f)
    else:
        wsgi = DebuggedApplication(app)

    run_simple(
        '0.0.0.0', port, wsgi,
        use_reloader=True,
        use_debugger=True,
    )


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
    except Exception as e:
        print('Database creation failed.')
        print('Exception message: {msg}'.format(msg=e.message))


@manager.command
def clear_cache():
    from everbean.core import cache
    with app.app_context():
        cache.clear()


@manager.command
def refresh_access_token():
    expires_time = int(time.time()) - 86400
    users = User.query.filter_by(
        enable_sync=True,
        douban_expires_at__lte=expires_time
    ).all()
    for user in users:
        tasks.refresh_douban_access_token.delay(user.id)


@manager.command
def sync_books():
    users = User.query.filter_by(enable_sync=True).all()
    for user in users:
        tasks.sync_books.delay(user.id)


@manager.command
def sync_notes():
    users = User.query.filter(
        User.enable_sync == True,
        User.evernote_access_token != None
    ).all()
    for user in users:
        tasks.sync_notes(user)


if __name__ == '__main__':
    manager.run()
