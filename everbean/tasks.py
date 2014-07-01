# coding=utf-8
from __future__ import (
    with_statement,
    absolute_import,
    unicode_literals
)
import time
from datetime import datetime

from flask import current_app as app
from flask.ext.mail import Message

from everbean.core import mail, db, celery
from everbean.models import User, Note
from everbean.ext.douban import (
    get_douban_client,
    import_annotations,
    import_books
)
from everbean.ext.evernote import (
    get_evernote_client,
    get_notebook,
    find_note,
    make_note,
    create_or_update_note
)


@celery.task
def send_mail(messages):
    if not (app.config['MAIL_SERVER'] and
            app.config['MAIL_USERNAME'] and
            app.config['MAIL_PASSWORD']):
        return False
    if isinstance(messages, Message):
        messages = [messages, ]
    with mail.connect() as conn:
        for msg in messages:
            conn.send(msg)


@celery.task
def refresh_douban_access_token(user_id):
    user = User.query.get(user_id)
    if not user:
        return
    client = get_douban_client()
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
        app.logger.error('Refresh token for user %s error.', user.douban_uid)


@celery.task
def sync_books(user_id):
    user = User.query.get(user_id)
    if not user:
        return
    import_books(user)


@celery.task
def import_douban_annotations(user_id):
    user = User.query.get(user_id)
    if not user:
        return
    import_annotations(user)


@celery.task
def sync_book_notes(user_id, book, notes=None):
    user = User.query.get(user_id)
    if not user or not user.evernote_access_token:
        return

    if notes is None:
        notes = Note.query.filter_by(
            user_id=user.id,
            book_id=book.id
        ).order_by(Note.created.asc()).all()

    if not notes:
        return

    # generate evernote format note
    token = user.evernote_access_token
    en = get_evernote_client(user.is_i18n, token)
    note_store = en.get_note_store()
    notebook = get_notebook(
        note_store,
        user.evernote_notebook,
        app.config['EVERNOTE_NOTEBOOK_NAME']
    )
    if not user.evernote_notebook:
        user.evernote_notebook = notebook.guid
        db.session.add(user)
        db.session.commit()

    note = None
    the_book = user.user_books.filter_by(book_id=book.id).first()
    if not the_book:
        return

    if the_book.evernote_guid:
        note = find_note(note_store, the_book.evernote_guid)

    note = make_note(
        book,
        notes,
        note,
        notebook,
        template=user.template
    )

    # sync to evernote
    note = create_or_update_note(note_store, note)
    # sync guid to database
    if note and hasattr(note, 'guid'):
        the_book.evernote_guid = note.guid

    the_book.updated = datetime.now()

    db.session.add(the_book)
    db.session.add(user)
    db.session.commit()


def sync_notes(user):
    def _sync_notes_of_book(book):
        notes = Note.query.filter_by(
            user_id=user.id,
            book_id=book.id
        ).order_by(Note.created.asc()).all()
        if notes:
            sync_book_notes.delay(user.id, book, notes)

    if not user.enable_sync:
        return
    books = user.books
    # now we can sync notes to evernote
    map(_sync_notes_of_book, books)
