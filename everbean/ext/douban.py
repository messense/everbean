# coding=utf-8
from __future__ import absolute_import, unicode_literals
import re
from datetime import datetime
import six
from flask import current_app as app
from douban_client.client import DoubanClient
from douban_client.api.error import DoubanAPIError
from everbean.core import db
from everbean.models import Book, Note, UserBook

_QUOTE_RE = re.compile(r'<原文开始>(.+)</原文结束>', re.S)


def small_book_cover(url):
    url = url.replace('mpic/', 'spic/')
    return url.replace('lpic/', 'spic/')


def medium_book_cover(url):
    url = url.replace('spic/', 'mpic/')
    return url.replace('lpic/', 'mpic/')


def large_book_cover(url):
    url = url.replace('mpic/', 'lpic/')
    return url.replace('spic/', 'lpic/')


def get_douban_client(token=None):
    client = DoubanClient(
        app.config['DOUBAN_API_KEY'],
        app.config['DOUBAN_API_SECRET'],
        app.config['DOUBAN_REDIRECT_URI'],
        app.config['DOUBAN_API_SCOPE']
    )
    if token:
        client.auth_with_token(token)
    return client


def get_douban_books(user, client=None, books=None,
                     start=0, count=100, recursive=True):
    client = client or get_douban_client(user.douban_access_token)
    books = books or []
    entrypoint = 'user/%s/collections?count=%i&start=%i'
    try:
        result = client.book.get(
            entrypoint % (
                user.douban_uid,
                count,
                start
            )
        )
    except DoubanAPIError as e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return books
    books.extend(result['collections'])
    total = result['total']
    real_count = len(result['collections'])
    if (total < count) or (start + real_count >= total) or (not recursive):
        return books
    start += count
    # retrieve books recursively
    books = get_douban_books(user, client, books, start, count)
    return books


def get_douban_annotations(user, client=None, annotations=None,
                           start=0, count=100, format='html',
                           recursive=True):
    client = client or get_douban_client(user.douban_access_token)
    annotations = annotations or []
    entrypoint = 'user/%s/annotations?count=%i' \
                 '&start=%i&format=%s&order=collect'
    try:
        annos = client.book.get(
            entrypoint % (
                user.douban_uid,
                count,
                start,
                format
            )
        )
    except DoubanAPIError as e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return annotations
    annotations.extend(annos['annotations'])
    total = annos['total']
    # annos['count'] is always 100, be careful
    real_count = len(annos['annotations'])
    if (total < count) or (start + real_count >= total) or (not recursive):
        return annotations
    start += count
    # retrieve annotations recursively
    annotations = get_douban_annotations(
        user, client, annotations,
        start, count, format
    )
    return annotations


def get_books_from_annotations(annotations):
    books = {}
    for annotation in annotations:
        book_id = annotation['book_id']
        if book_id not in books:
            books[book_id] = {
                'id': book_id,
                'title': annotation['book']['title'].strip(),
                'author': ', '.join(annotation['book']['author']),
                'alt': annotation['book']['alt'],
                'cover': annotation['book']['image'],
                'pubdate': annotation['book']['pubdate'],
                'summary': annotation['book']['summary'],
                'annotations': [],
            }
        note = {
            'id': annotation['id'],
            'chapter': annotation['chapter'],
            'summary': annotation['summary'],
            'content': annotation['content'],
            'time': datetime.strptime(annotation['time'],
                                      '%Y-%m-%d %H:%M:%S'),
            'page_no': int(annotation['page_no']),
            'privacy': int(annotation['privacy']),
        }
        # reverse notes
        books[book_id]['annotations'].insert(0, note)
    return books


def import_books(user, client=None):
    client = client or get_douban_client(user.douban_access_token)
    books = get_douban_books(user, client)
    for book in books:
        the_book = Book.query.filter_by(
            douban_id=book['book_id']
        ).first()
        if not the_book:
            # create the book
            the_book = Book()
            the_book.douban_id = book['book_id']
            the_book.title = book['book']['title'][:100]
            the_book.author = ', '.join(book['book']['author'])[:100]
            the_book.cover = book['book']['image']
            the_book.pubdate = book['book']['pubdate']
            the_book.summary = book['book']['summary']
            db.session.add(the_book)
            db.session.commit()

        user_book = UserBook.query.filter_by(
            user_id=user.id,
            book_id=the_book.id
        ).first()
        # if not User.query.filter(id == user.id,
        #                          User.books.any(id=the_book.id)):
        if not user_book:
            UserBook(user, the_book, datetime.now(), book['status'])
        else:
            if user_book.status != book['status']:
                user_book.status = book['status']
                user_book.updated = datetime.now()
        db.session.add(user_book)
        db.session.add(user)
        db.session.flush()
    db.session.commit()


def import_annotations(user, client=None):
    client = client or get_douban_client(user.douban_access_token)
    annotations = get_douban_annotations(user, client)
    books = get_books_from_annotations(annotations)
    for book in six.itervalues(books):
        the_book = Book.query.filter_by(douban_id=book['id']).first()
        if not the_book:
            # create the book
            the_book = Book()
            the_book.douban_id = book['id']
            the_book.title = book['title'][:100]
            the_book.author = book['author'][:100]
            the_book.cover = book['cover']
            the_book.pubdate = book['pubdate']
            the_book.summary = book['summary']
            db.session.add(the_book)
            db.session.commit()

        for annotation in book['annotations']:
            note = Note.query.filter_by(
                douban_id=annotation['id'],
                user_id=user.id
            ).first()
            if not note:
                # create the note
                note = Note()
                note.douban_id = annotation['id']
                note.user_id = user.id
                note.book_id = the_book.id
                note.chapter = annotation['chapter'][:100]
                note.summary = annotation['summary']
                note.content_html = annotation['content']
                note.created = annotation['time']
                note.updated = annotation['time']
                note.page_no = annotation['page_no']
                note.private = False
                if annotation['privacy'] == 1:
                    note.private = True
                the_book.notes.append(note)
                db.session.flush()
        db.session.commit()


def get_annotation(user, douban_id, client=None, format='text'):
    client = client or get_douban_client(user.douban_access_token)
    entrypoint = 'annotation/%s?format=%s' % (douban_id, format)
    annotation = None
    try:
        annotation = client.book.get(entrypoint)
    except DoubanAPIError as e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
    return annotation


def create_annotation(user, note, client=None):
    if note.douban_id:
        return note
    client = client or get_douban_client(user.douban_access_token)
    entrypoint = '/v2/book/%s/annotations' % note.book.douban_id
    privacy = 'public'
    if note.private:
        privacy = 'private'
    data = dict(
        content=note.content,
        privacy=privacy
    )
    if note.page_no > 0:
        data['page'] = note.page_no
    else:
        data['chapter'] = note.chapter
    try:
        result = client.book._post(entrypoint, **data)
    except DoubanAPIError as e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return False

    note.douban_id = result['id']
    note.summary = result['summary']
    annotation = get_annotation(user, note.douban_id, client, format='html')
    note.content_html = annotation['content']
    db.session.add(note)
    db.session.commit()
    return note


def update_annotation(user, note, client=None):
    if not note.douban_id:
        return False
    client = client or get_douban_client(user.douban_access_token)
    entrypoint = '/v2/book/annotation/%s' % note.douban_id
    privacy = 'public'
    if note.private:
        privacy = 'private'
    data = dict(
        content=note.content,
        privacy=privacy
    )
    if note.page_no > 0:
        data['page'] = note.page_no
    else:
        data['chapter'] = note.chapter
    try:
        result = client.book._put(entrypoint, **data)
    except DoubanAPIError as e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return False

    note.summary = result['summary']
    annotation = get_annotation(user,
                                note.douban_id,
                                client,
                                format='html')
    note.content_html = annotation['content']
    db.session.add(note)
    db.session.commit()
    return note


def delete_annotation(user, note, client=None):
    if not note.douban_id:
        return False
    client = client or get_douban_client(user.douban_access_token)
    entrypoint = '/v2/book/annotation/%s' % note.douban_id
    try:
        client.book._delete(entrypoint)
    except DoubanAPIError as e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return False
    except ValueError:
        return True
    return True


def content_to_html(content):
    def _make_quote(match):
        text = match.group(1)
        return '<blockquote><q>%s</q></blockquote>' % text

    content = _QUOTE_RE.sub(_make_quote, content)

    return content