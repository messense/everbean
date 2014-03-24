#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function, with_statement
import os
from flask import Flask
from .utils import parse_command_line
from .models.user import User
from .core import db, login_manager


def create_app(config=None, envvar="everbean_config"):
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(BASEDIR, "static"),
        template_folder="templates"
    )

    load_configuration(app, config, envvar)
    register_extensions(app)
    register_hooks(app)
    register_blueprints(app)
    setup_extensions(app)

    return app


def load_configuration(app, config, envvar):
    # load default configuration first
    app.config.from_object('everbean.defaults')
    if config is not None:
        if config.endswith('.py'):
            try:
                app.config.from_pyfile(config)
            except IOError:
                app.logger.warning("Cannot load configuration from python file %s" % config)
        else:
            app.config.from_object(config)
    if envvar is not None:
        try:
            app.config.from_envvar(envvar)
        except RuntimeError:
            app.logger.warning("Environment var %s is not set." % envvar)
    parse_command_line(app)

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

    db.init_app(app)
    login_manager.init_app(app)
    
    if app.debug:
        from flask.ext.debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)


def setup_extensions(app):
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(douban_id=user_id).first()

    login_manager.login_view = "account.login"


def register_blueprints(app):
    from .handlers.account import account
    from .handlers.home import home

    app.register_blueprint(home)
    app.register_blueprint(account)


if __name__ == '__main__':
    app = create_app()
    app.run()
