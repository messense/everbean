# coding=utf-8
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template
from flask.ext.login import current_user, login_required
from everbean.core import cache
from everbean.models import User, Book, Note
from everbean.utils import ObjectDict

bp = Blueprint('user', __name__, url_prefix='/u')


@bp.route('/<uid>')
@login_required
def index(uid):
    @cache.memoize(300)
    def _get_wish_books(user_id):
        return Book.query.filter(
            Book.user_books.any(user_id=user_id, status='wish')
        ).limit(6).all()

    @cache.memoize(300)
    def _get_reading_books(user_id):
        return Book.query.filter(
            Book.user_books.any(user_id=user_id, status='reading')
        ).limit(6).all()

    @cache.memoize(300)
    def _get_read_books(user_id):
        return Book.query.filter(
            Book.user_books.any(user_id=user_id, status='read')
        ).limit(6).all()

    @cache.memoize(300)
    def _get_recent_notes(user_id):
        return Note.query.options(joinedload('book')).filter_by(
            user_id=user_id
        ).order_by(Note.created.desc()).limit(8).all()

    if current_user.douban_uid == uid:
        user = current_user
    else:
        user = User.query.filter_by(douban_uid=uid).first_or_404()

    books = ObjectDict()
    books.wish = _get_wish_books(user.id)
    books.reading = _get_reading_books(user.id)
    books.read = _get_read_books(user.id)

    notes = _get_recent_notes(user.id)

    return render_template(
        'user/index.html',
        user=user,
        books=books,
        notes=notes
    )
