#!/usr/bin/env python
# coding=utf-8
from celery import Celery
from everbean.ext import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.assets import Environment, Bundle
from flask.ext.mail import Mail

# database
db = SQLAlchemy()

# celery
celery = Celery()

# flask-login
login_manager = LoginManager()

# flask-mail
mail = Mail()

# flask-assets
assets = Environment()

js_all = Bundle('js/jquery.min.js',
                'js/turbolinks.js',
                'js/bootstrap.min.js',
                'js/turbolinks-indicter.js',
                filters='rjsmin',
                output='js/all.js')
assets.register('js_all', js_all)

css_all = Bundle('css/bootstrap.min.css',
                 'css/style.css',
                 filters='cssmin',
                 output='css/all.css')

assets.register('css_all', css_all)

