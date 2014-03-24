#!/usr/bin/env python
# coding=utf-8

from ..core import db


class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    douban_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    evernote_guid = db.Column(db.String(36))
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    cover = db.Column(db.String(200))
    pubdate = db.Column(db.String(10))
    summary = db.Column(db.Text)
    enable_sync = db.Column(db.Boolean, default=True)
    updated = db.Column(db.DateTime)
    status = db.Column(db.String(7), nullable=False, default="reading")