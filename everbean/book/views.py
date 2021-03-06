# coding=utf-8
from __future__ import absolute_import, unicode_literals

from sqlalchemy.orm import load_only, joinedload
from flask import Blueprint, render_template
from flask import redirect, abort, request, url_for
from flask.ext.login import current_user, login_required

from ..account.models import User
from ..note.models import Note
from ..core import cache, db
from ..utils import ObjectDict
from ..ext.evernote import (
    generate_enml_makeup,
    enml_to_html,
    get_template_name
)
from ..ext.douban import get_book

from .models import Book


blueprint = Blueprint('book', __name__, url_prefix='/book')


@blueprint.route('/<int:book_id>')
def index(book_id):
    @cache.memoize(300)
    def _get_book(bk_id):
        return Book.query.get_or_404(bk_id)

    @cache.memoize(300)
    def _get_notes(bk_id, count=10):
        return Note.query.options(joinedload('user').load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
        )).filter_by(
            book_id=bk_id
        ).order_by(Note.created.desc()).limit(count).all()

    @cache.memoize(300)
    def _get_wish_users(bk_id):
        return User.query.options(load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
        )).filter(
            User.user_books.any(book_id=bk_id, status='wish')
        ).limit(12).all()

    @cache.memoize(300)
    def _get_reading_users(bk_id):
        return User.query.options(load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
        )).filter(
            User.user_books.any(book_id=bk_id, status='reading')
        ).limit(12).all()

    @cache.memoize(300)
    def _get_read_users(bk_id):
        return User.query.options(load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
        )).filter(
            User.user_books.any(book_id=bk_id, status='read')
        ).limit(12).all()

    @cache.memoize(300)
    def _get_noted_users(bk_id):
        return User.query.options(load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
        )).filter(
            User.notes.any(book_id=bk_id)
        ).limit(12).all()

    book = _get_book(book_id)
    book_notes = _get_notes(book_id)
    users = ObjectDict()
    users.wish = _get_wish_users(book_id)
    users.reading = _get_reading_users(book_id)
    users.read = _get_read_users(book_id)
    users.noted = _get_noted_users(book_id)

    return render_template(
        'book/index.html',
        book=book,
        notes=book_notes,
        users=users,
    )


@blueprint.route('/<int:book_id>/notes')
@blueprint.route('/<int:book_id>/notes/<int:page>')
def notes(book_id, page=1):
    book = Book.query.get_or_404(book_id)
    book_notes = Note.query.options(joinedload('user')).filter_by(
        book_id=book_id
    ).order_by(Note.created.desc())
    pager = book_notes.paginate(page)
    return render_template('book/notes.html',
                           book=book,
                           pager=pager)


@blueprint.route('/<int:book_id>/<uid>/notes')
@login_required
def preview(book_id, uid, template='default'):
    if current_user.douban_uid == uid:
        user = current_user
    else:
        user = User.query.filter_by(douban_uid=uid).first_or_404()
    book = Book.query.get_or_404(book_id)
    book_notes = Note.query.filter_by(
        user_id=user.id,
        book_id=book.id
    )
    if current_user.douban_uid != uid:
        book_notes = book_notes.filter_by(private=False)
    book_notes = book_notes.order_by(Note.created.asc()).all()

    if not book_notes:
        abort(404)

    template = request.args.get('template', template)
    template = get_template_name(template)

    enml = generate_enml_makeup(book, book_notes, template)
    body = enml_to_html(enml)
    return render_template('book/preview.html',
                           user=user,
                           book=book,
                           body=body)


@blueprint.route('/search/<int:book_id>')
def search(book_id):
    book = Book.query.filter_by(douban_id=book_id).first()
    if not book:
        if current_user.is_authenticated():
            # add to database
            the_book = get_book(book_id, current_user)
            if the_book:
                book = Book()
                book.douban_id = book_id
                book.title = the_book['title'][:100]
                book.author = ', '.join(the_book['author'])[:100]
                book.cover = the_book['image']
                book.pubdate = the_book['pubdate']
                book.summary = the_book['summary']
                db.session.add(book)
                db.session.commit()
                return redirect(url_for('book.index', book_id=book.id))
            else:
                abort(404)
        else:
            # redirect to douban
            return redirect('http://book.douban.com/subject/{book_id}/'.format(
                book_id=book_id
            ))
    else:
        return redirect(url_for('book.index', book_id=book.id))
