#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function, with_statement, absolute_import
import os
from flask import Flask, url_for
from everbean.utils import parse_command_line, parse_config_file
from everbean.models.user import User
from everbean.core import db, celery, cache, login_manager, assets, mail


def create_app(config=None, envvar="everbean_config"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, "static"),
        template_folder="templates"
    )

    load_configuration(app, config, envvar)
    register_extensions(app)
    register_hooks(app)
    register_template_utils(app)
    register_blueprints(app)
    setup_extensions(app)

    return app


def load_configuration(app, config, envvar):
    # load default configuration first
    app.config.from_object('everbean.defaults')
    if config is None:
        # if current directory has a config.py file, try to load it
        cwd = os.path.join(os.getcwd(), 'config.py')
        if os.path.exists(cwd):
            config = cwd
    if config is not None:
        parse_config_file(app, config)

    if envvar is not None:
        try:
            app.config.from_envvar(envvar)
        except RuntimeError:
            pass

    cfg = parse_command_line(app, None, final=False)
    if cfg.get('SETTINGS'):
        parse_config_file(app, cfg['SETTINGS'])
    # update app.config with command line arguments
    app.config.update(cfg)

    # check config
    for name in (
            'DOUBAN_API_KEY', 'DOUBAN_API_SECRET', 'DOUBAN_REDIRECT_URI', 'EVERNOTE_CONSUMER_KEY',
            'EVERNOTE_CONSUMER_SECRET',
            'SQLALCHEMY_DATABASE_URI'):
        if not app.config[name]:
            print("Configuration %s is not set, application may not work as expected." % name)


def register_hooks(app):
    @app.before_request
    def before_request():
        pass

    @app.teardown_appcontext
    def teardown_app(error):
        pass


def register_extensions(app):
    from flask.ext.turbolinks import turbolinks

    db.init_app(app)
    cache.init_app(app)
    celery.config_from_object(app.config)
    login_manager.init_app(app)
    mail.init_app(app)
    turbolinks(app)
    assets.init_app(app)

    if app.debug:
        # load debug toobar
        from flask.ext.debugtoolbar import DebugToolbarExtension
        # disable redirection interception of Flask-DebugToobar
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        DebugToolbarExtension(app)


def setup_extensions(app):
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(douban_id=user_id).first()

    login_manager.login_view = "account.login"


def register_template_utils(app):
    @app.template_global('static_url')
    def static_url(f):
        # shortcut for url_for('static', filename=xxx)
        return url_for('static', filename=f)


def register_blueprints(app):
    from everbean.handlers import home
    from everbean.handlers import account
    from everbean.handlers import user
    from everbean.handlers import oauth

    app.register_blueprint(home.bp)
    app.register_blueprint(account.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(oauth.bp)


