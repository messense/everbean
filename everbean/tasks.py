# coding=utf-8
from __future__ import with_statement
from datetime import datetime
from flask import current_app as app
from flask.ext.mail import Message
from douban_client.api.error import DoubanAPIError
from everbean.core import mail, db, celery
from everbean.models import User, Book
from everbean.utils import get_douban_client


@celery.task
def send_mail(messages):
    if isinstance(messages, Message):
        messages = [messages, ]
    with mail.connect() as conn:
        for msg in messages:
            conn.send(msg)


@celery.task
def sync_books(user):
    client = get_douban_client(app, user.douban_access_token)
    entrypoint = 'user/%s/collections' % user.douban_uid
    try:
        books = client.book.get(entrypoint)
    except DoubanAPIError, e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return
    collections = books['collections']
    book_ids = []
    # update database
    for book in collections:
        book_ids.append(int(book['book_id']))
        the_book = Book.query.filter_by(user_id=user.id, douban_id=book['book_id']).first()
        if the_book:
            # update book
            the_book.status = book['status']
            the_book.enable_sync = user.enable_sync
            the_book.updated = datetime.strptime(book['updated'], '%Y-%m-%d %H:%M:%S')
        else:
            # create a new book record
            the_book = Book()
            the_book.user_id = user.id
            the_book.douban_id = int(book['book_id'])
            the_book.status = book['status']
            the_book.author = book['book']['author'][0]
            the_book.cover = book['book']['images']['medium']
            the_book.enable_sync = user.enable_sync
            the_book.pubdate = book['book']['pubdate']
            the_book.summary = book['book']['summary']
            the_book.title = book['book']['title']
            the_book.updated = datetime.strptime(book['updated'], '%Y-%m-%d %H:%M:%S')

        db.session.add(the_book)
        db.session.commit()
    # clean database
    old_books = Book.query.filter_by(user_id=user.id)
    for book in old_books:
        if book.douban_id not in book_ids:
            db.session.delete(book)

    db.session.commit()


@celery.task
def find_books(user):
    pass


@celery.task
def sync_notes(user, book):
    pass