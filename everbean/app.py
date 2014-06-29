#!/usr/bin/env python
# coding=utf-8
from __future__ import (
    print_function, with_statement,
    absolute_import, unicode_literals
)
import os
import time
import logging
from flask import Flask, url_for, render_template, g
from jinja2 import MemcachedBytecodeCache
from everbean.utils import parse_config_file
from everbean.models import User
from everbean.core import login_manager, cache


def create_app(config=None, envvar='everbean_config', debug=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, 'static'),
        template_folder='templates'
    )

    load_configuration(app, config, envvar, debug)
    register_extensions(app)
    register_hooks(app)
    register_template_utils(app)
    register_blueprints(app)
    setup_extensions(app)

    if not app.debug:
        register_errorhandlers(app)

    return app


def load_configuration(app, config, envvar, debug):
    # load default configuration first
    app.config.from_object('everbean.defaults')
    if config is None:
        # if current directory has a config.py file, try to load it
        cwd = os.path.join(os.getcwd(), 'config.py')
        if os.path.exists(cwd):
            config = cwd
    if isinstance(config, dict):
        app.config.update(config)
    else:
        parse_config_file(app, config)

    if envvar is not None:
        try:
            app.config.from_envvar(envvar)
        except RuntimeError:
            pass
    # reset debug
    if debug:
        app.debug = True


def register_hooks(app):
    @app.before_first_request
    def setup_logging():
        if not app.debug:
            # In production mode, add log handler to sys.stderr.
            app.logger.addHandler(logging.StreamHandler())
            app.logger.setLevel(logging.INFO)


def register_errorhandlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_note_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500


def register_extensions(app):
    from flask.ext.turbolinks import turbolinks
    from everbean.core import db, celery, assets
    from everbean.core import mail, limiter

    db.init_app(app)
    cache.init_app(app)
    celery.config_from_object(app.config)
    login_manager.init_app(app)
    mail.init_app(app)
    turbolinks(app)
    assets.init_app(app)
    limiter.init_app(app)

    if app.config['USE_SERVER_SIDE_SESSION']:
        from flask.ext.session import Session
        Session(app)

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

    login_manager.login_view = 'account.login'


def register_template_utils(app):
    from everbean.ext.douban import small_book_cover
    from everbean.ext.douban import medium_book_cover
    from everbean.ext.douban import large_book_cover

    @app.template_global('static_url')
    def static_url(f):
        # shortcut for url_for('static', filename=xxx)
        return url_for('static', filename=f)
    if not app.debug:
        app.jinja_env.bytecode_cache = MemcachedBytecodeCache(cache)
    app.jinja_env.filters['small_book_cover'] = small_book_cover
    app.jinja_env.filters['medium_book_cover'] = medium_book_cover
    app.jinja_env.filters['large_book_cover'] = large_book_cover


def register_blueprints(app):
    from everbean.handlers import home
    from everbean.handlers import account
    from everbean.handlers import user
    from everbean.handlers import oauth
    from everbean.handlers import book
    from everbean.handlers import note
    from everbean.handlers import api

    app.register_blueprint(home.bp)
    app.register_blueprint(account.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(oauth.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(note.bp)
    app.register_blueprint(api.bp)
