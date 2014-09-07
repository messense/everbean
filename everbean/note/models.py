# coding=utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime, Boolean, Text
from flask import url_for

from everbean.core import db


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
