#!/usr/bin/env python
# coding=utf-8
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

# database
db = SQLAlchemy()

# flask-login
login_manager = LoginManager()
