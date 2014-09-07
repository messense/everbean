# coding=utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime, Boolean, Text
from sqlalchemy.orm import relationship, backref
from flask import url_for

from ..core import db
from ..utils import to_bytes
from ..note.models import Note


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
        'User',
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
