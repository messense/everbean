# coding=utf-8
from __future__ import with_statement, absolute_import
from datetime import datetime
from flask import current_app as app
from flask.ext.mail import Message
from douban_client.api.error import DoubanAPIError
import evernote.edam.type.ttypes as Types
from everbean.core import mail, db, celery
from everbean.models import Book
from everbean.utils import get_douban_client, get_books_from_annotations, get_douban_annotations
from everbean.evernote import get_evernote_client, get_notebook, find_note, make_note, create_or_update_note


@celery.task
def send_mail(messages):
    if isinstance(messages, Message):
        messages = [messages, ]
    with mail.connect() as conn:
        for msg in messages:
            conn.send(msg)


@celery.task
def refresh_douban_access_token(user):
    client = get_douban_client(app)
    client.refresh_token(user.douban_refresh_token)
    me = client.user.me
    if 'id' in me:
        # update access token and other infomations
        user.douban_access_token = client.token_code
        user.douban_refresh_token = client.refresh_token_code
        user.douban_expires_at = client.access_token.expires_at
        user.douban_name = me['name']
        user.avatar = me['avatar']
        user.large_avatar = me['avatar'].replace('icon/u', 'icon/ul')
        user.signature = me['signature']
        user.desc = me['desc']

        db.session.add(user)
        db.session.commit()
    else:
        app.logger.warning('Refresh token for user %s error.' % user.douban_uid)


@celery.task
def sync_books(user):
    """ Sync reading status books """
    client = get_douban_client(app, user.douban_access_token)
    entrypoint = 'user/%s/collections?count=100&status=reading' % user.douban_uid
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
            the_book.author = ', '.join(book['book']['author'])
            the_book.cover = book['book']['images']['medium']
            the_book.enable_sync = user.enable_sync
            the_book.pubdate = book['book']['pubdate']
            the_book.summary = book['book']['summary']
            the_book.title = book['book']['title']
            the_book.updated = datetime.strptime(book['updated'], '%Y-%m-%d %H:%M:%S')

        db.session.add(the_book)
        db.session.commit()
    # clean database
    old_books = Book.query.filter_by(user_id=user.id).all()
    for book in old_books:
        if book.status == 'read':
            continue
        if book.douban_id not in book_ids and not book.evernote_guid:
            db.session.delete(book)

    db.session.commit()


@celery.task
def sync_notes(user):
    if not user.enable_sync:
        return
    annotations = get_douban_annotations(app, user)
    books = get_books_from_annotations(annotations)

    # now we can sync notes to evernote
    for book_id in books:
        book = books[book_id]
        sync_book_notes.delay(user, book)


@celery.task
def sync_book_notes(user, book):
    if not user.evernote_access_token:
        return
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
        the_book.author = ', '.join(a_book['author'])
        the_book.cover = a_book['images']['medium']
        the_book.enable_sync = True
        the_book.pubdate = a_book['pubdate']
        the_book.summary = a_book['summary']
        the_book.title = a_book['title']
        the_book.updated = datetime.strptime(a_book['current_user_collection']['updated'],
                                             '%Y-%m-%d %H:%M:%S')

    # generate evernote format note
    token = user.evernote_access_token
    en = get_evernote_client(app, user.is_i18n, token)
    note_store = en.get_note_store()
    notebook = get_notebook(note_store, the_book.evernote_guid, str(app.config['EVERNOTE_NOTEBOOK_NAME']), token)
    if not user.evernote_notebook:
        user.evernote_notebook = notebook.guid
        db.session.add(user)
    if the_book.evernote_guid:
        note = find_note(note_store, the_book.evernote_guid, token)
    note = make_note(the_book, note, notebook)
    # sync to evernote
    create_or_update_note(note_store, note, token)

    db.session.add(the_book)
    db.session.commit()