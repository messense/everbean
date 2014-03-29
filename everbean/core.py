#!/usr/bin/env python
# coding=utf-8
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.assets import Environment, Bundle

# database
db = SQLAlchemy()

# flask-login
login_manager = LoginManager()

# flask-assets
assets = Environment()

js_all = Bundle('js/jquery.min.js',
                'js/turbolinks.js',
                'js/bootstrap.min.js',
                filters='rjsmin',
                output='js/all.js')
assets.register('js_all', js_all)

css_all = Bundle('css/bootstrap.min.css',
                 'css/style.css',
                 filters='cssmin',
                 output='css/all.css')

assets.register('css_all', css_all)

