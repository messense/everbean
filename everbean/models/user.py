#!/usr/bin/env python
# coding=utf-8
from everbean.core import db
from flask.ext.login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    douban_name = db.Column(db.String(50), nullable=False)
    douban_id = db.Column(db.String(20), nullable=False)
    large_avatar = db.Column(db.String(200))
    avatar = db.Column(db.String(200))
    signature = db.Column(db.String(500))
    desc = db.Column(db.String(500))
    douban_uid = db.Column(db.String(20), nullable=False)
    douban_alt = db.Column(db.String(200))
    douban_access_token = db.Column(db.CHAR(32), nullable=False)
    douban_refresh_token = db.Column(db.CHAR(32), nullable=False)
    created = db.Column(db.DateTime)
    douban_expires_at = db.Column(db.Integer)
    evernote_username = db.Column(db.String(50))
    evernote_access_token = db.Column(db.String(200))
    is_i18n = db.Column(db.Boolean, default=False)
    enable_sync = db.Column(db.Boolean, default=True)

    def get_id(self):
        return self.douban_id
