# coding=utf-8
from sqlalchemy.orm import load_only, joinedload
from flask import Blueprint, render_template
from flask.ext.login import current_user, login_required
from everbean.models import Book, Note, User
from everbean.core import cache
from everbean.utils import ObjectDict

bp = Blueprint('book', __name__, url_prefix='/book')


@bp.route('/<int:book_id>')
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
            'signature',
        )).filter(
            User.user_books.any(book_id=bk_id, status='wish')
        ).limit(9).all()

    @cache.memoize(300)
    def _get_reading_users(bk_id):
        return User.query.options(load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
            'signature',
        )).filter(
            User.user_books.any(book_id=bk_id, status='reading')
        ).limit(9).all()

    @cache.memoize(300)
    def _get_read_users(bk_id):
        return User.query.options(load_only(
            'id',
            'douban_uid',
            'douban_name',
            'avatar',
            'large_avatar',
            'signature',
        )).filter(
            User.user_books.any(book_id=bk_id, status='read')
        ).limit(9).all()

    book = _get_book(book_id)
    notes = _get_notes(book_id)
    users = ObjectDict()
    users.wish = _get_wish_users(book_id)
    users.reading = _get_reading_users(book_id)
    users.read = _get_read_users(book_id)

    return render_template(
        'book/index.html',
        book=book,
        notes=notes,
        users=users,
    )
