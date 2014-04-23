# coding=utf-8
from flask import Blueprint, render_template
from flask.ext.login import current_user, login_required
from everbean.models import Book
from everbean.core import cache

bp = Blueprint('book', __name__, url_prefix='/book')


@bp.route('/<int:book_id>')
def index(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book/index.html', book=book)
