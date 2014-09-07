# coding=utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime, Boolean, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from flask import url_for
from flask.ext.login import UserMixin

from ..core import db
from ..note.models import Note


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    douban_name = Column(String(50), nullable=False)
    douban_id = Column(String(20), nullable=False, unique=True)
    large_avatar = Column(String(200))
    avatar = Column(String(200))
    signature = Column(String(500))
    desc = Column(String(500))
    douban_uid = Column(String(20), nullable=False, unique=True)
    douban_alt = Column(String(200))
    douban_access_token = Column(CHAR(32), nullable=False)
    douban_refresh_token = Column(CHAR(32), nullable=False)
    created = Column(DateTime, default=datetime.now)
    douban_expires_at = Column(Integer, index=True)
    evernote_username = Column(String(50))
    evernote_access_token = Column(String(200))
    evernote_notebook = Column(String(36))
    is_i18n = Column(Boolean, default=False)
    enable_sync = Column(Boolean, default=True, index=True)
    email = Column(String(50), unique=True)
    email_verify_code = Column(CHAR(32), unique=True)
    email_verified = Column(Boolean, default=False, index=True)
    template = Column(String(20), default='default')

    # user - books Many-to-many
    books = association_proxy('user_books', 'book')
    # user - notes One-to-many
    notes = relationship(
        'Note',
        backref='user',
        cascade='all, delete-orphan',
        lazy="dynamic",
        order_by=lambda: Note.created.desc()
    )

    def get_id(self):
        return self.douban_id

    @property
    def absolute_url(self):
        return url_for('user.index', uid=self.douban_uid)

    def __repr__(self):
        return b'<User({uid})>'.format(uid=self.douban_uid)
