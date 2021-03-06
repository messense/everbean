# coding=utf-8
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, render_template

from ..utils import ObjectDict
from ..book.models import Book
from ..core import cache


blueprint = Blueprint('home', __name__, url_prefix='/')


@blueprint.route('/')
def index():
    @cache.cached(timeout=300, key_prefix='reading_books_12')
    def _reading_books():
        return Book.query.filter(
            Book.user_books.any(status='reading')
        ).limit(12).all()

    @cache.cached(timeout=300, key_prefix='read_books_12')
    def _read_books():
        return Book.query.filter(
            Book.user_books.any(status='read')
        ).limit(12).all()

    @cache.cached(timeout=300, key_prefix='wish_books_12')
    def _wish_books():
        return Book.query.filter(
            Book.user_books.any(status='wish')
        ).limit(12).all()

    books = ObjectDict()
    books.reading = _reading_books()
    books.read = _read_books()
    books.wish = _wish_books()
    return render_template('home/index.html', books=books)


@blueprint.route('about')
def about():
    import everbean
    return render_template('home/about.html', version=everbean.__version__)


@blueprint.route('faq')
def faq():
    return render_template('home/faq.html')
