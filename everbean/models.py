# coding=utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime, Boolean, CHAR, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from flask import url_for
from flask.ext.login import UserMixin
from everbean.core import db
from everbean.utils import to_bytes


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


class UserBook(db.Model):
    __tablename__ = 'user_book'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    evernote_guid = Column(String(36))
    updated = Column(DateTime, index=True, default=datetime.now)
    status = Column(String(7), nullable=False, default="reading", index=True)
    enable_sync = Column(Boolean, default=True, index=True)

    # bidirectional attribute/collection of "user"/"user_books"
    user = relationship(
        User,
        backref=backref(
            'user_books',
            lazy='dynamic',
            cascade='all, delete-orphan'
        )
    )

    # reference to the "Book" object
    book = relationship(
        'Book',
        backref=backref(
            'user_books',
            lazy='dynamic',
            cascade='all, delete-orphan'
        )
    )

    def __init__(self, user, book,
                 updated=None, status='reading',
                 enable_sync=True, evernote_guid=None):
        self.user = user
        self.book = book
        self.updated = updated or datetime.now()
        self.status = status
        self.enable_sync = enable_sync
        self.evernote_guid = evernote_guid

    def __repr__(self):
        return b'<UserBook({user_id}, {book_id})>'.format(
            user_id=self.user_id,
            book_id=self.book_id
        )


class Book(db.Model):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    douban_id = Column(String(20), nullable=False, unique=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    cover = Column(String(200))
    pubdate = Column(String(20))
    summary = Column(Text)

    notes = relationship(
        'Note',
        backref='book',
        cascade='all, delete-orphan',
        lazy="dynamic",
        order_by=lambda: Note.created.desc()
    )

    @property
    def alt(self):
        if self.douban_id:
            return 'http://book.douban.com/subject/{id}'.format(id=self.douban_id)
        return ''

    @property
    def absolute_url(self):
        return url_for('book.index', book_id=self.id)

    def __repr__(self):
        return b'<Book({id}, {title})>'.format(
            id=self.id,
            title=to_bytes(self.title)
        )


class Note(db.Model):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True)
    douban_id = Column(String(20), unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    book_id = Column(Integer, ForeignKey('book.id'), index=True)
    chapter = Column(String(100))
    summary = Column(Text)
    content = Column(Text)
    content_html = Column(Text)
    page_no = Column(Integer, default=0)
    created = Column(DateTime, default=datetime.now, index=True)
    updated = Column(DateTime)
    private = Column(Boolean, default=False)

    @property
    def alt(self):
        if self.douban_id:
            return 'http://book.douban.com/annotation/{id}/'.format(id=self.douban_id)
        return ''

    @property
    def absolute_url(self):
        return url_for('note.index', note_id=self.id)

    def __repr__(self):
        return b'<Note({id}, {book_id}, {douban_id})>'.format(
            id=self.id,
            book_id=self.book_id,
            douban_id=self.douban_id
        )
