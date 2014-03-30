# coding=utf-8
from __future__ import with_statement
from datetime import datetime
from flask import current_app as app
from flask.ext.mail import Message
from douban_client.api.error import DoubanAPIError
from everbean.core import mail, db, celery
from everbean.models import Book
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
        if book.douban_id not in book_ids and not book.evernote_guid:
            db.session.delete(book)

    db.session.commit()


@celery.task
def sync_notes(user):
    if not user.enable_sync:
        return
    client = get_douban_client(app, user.douban_access_token)
    entrypoint = 'user/%s/annotations' % user.douban_uid
    try:
        annotations = client.book.get(entrypoint)
    except DoubanAPIError, e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return
    total = int(annotations['total'])
    try:
        annotations = client.book.get(entrypoint, total=total)
    except DoubanAPIError, e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return
    annotations = annotations['annotations']
    books = {}
    for annotation in annotations:
        book_id = annotation['book_id']
        if book_id not in books:
            books[book_id] = {
                'book_id': book_id,
                'title': annotation['book']['title'],
                'subtitle': annotation['book']['subtitle'],
                'author': annotation['book']['author'],
                'alt': annotation['book']['alt'],
                'cover': annotation['book']['image'],
                'annotations': [],
            }
        note = {
            'chapter': annotation['chapter'],
            'summary': annotation['summary'],
            'content': annotation['content'],
            'time': annotation['time'],
            'page_no': int(annotation['page_no']),
        }
        # reverse notes
        books[book_id]['annotations'].insert(0, note)

    # now we can sync notes to evernote
    for book_id in books:
        book = books[book_id]
        sync_book_notes.delay(user, book)


@celery.task
def sync_book_notes(user, book):
    the_book = Book.query.filter_by(douban_id=book['book_id']).first()
    if the_book:
        pass
    else:
        client = get_douban_client(app, user.douban_access_token)
        try:
            a_book = client.book.get(book['book_id'])
        except DoubanAPIError, e:
            app.logger.error('DoubanAPIError status: %s' % e.status)
            app.logger.error('DoubanAPIError reason: %s' % e.reason)
            return
        the_book = Book()
        the_book.user_id = user.id
        the_book.douban_id = int(book['book_id'])
        the_book.status = a_book['current_user_collection']['status']
        the_book.author = a_book['author'][0]
        the_book.cover = a_book['images']['medium']
        the_book.enable_sync = True
        the_book.pubdate = a_book['pubdate']
        the_book.summary = a_book['summary']
        the_book.title = a_book['title']
        the_book.updated = datetime.strptime(a_book['current_user_collection']['updated'],
                                             '%Y-%m-%d %H:%M:%S')

    # generate evernote format note

    # sync to evernote

    db.session.add(the_book)
    db.session.commit()