# coding=utf-8
from __future__ import absolute_import, unicode_literals
import json
import functools
from flask import Blueprint, jsonify as flask_jsonify
from flask import request, Response, url_for
from flask.ext.login import current_user
from everbean.models import Book
from everbean.ext.douban import search_or_get_books


bp = Blueprint('api', __name__, url_prefix='/api')


def jsonify(*args, **kwargs):
    if args and len(args) == 1 and not kwargs and isinstance(args[0], list):
        s = json.dumps(args[0])
        return Response(s, mimetype='application/json')
    else:
        return flask_jsonify(*args, **kwargs)


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated():
            return func(*args, **kwargs)
        else:
            return jsonify(
                error=1,
                message='请先登录！'
            )
    return wrapper


@bp.route('/book/search')
def book_search():
    keyword = request.args.get('q', None)
    if keyword is None:
        return jsonify([])
    books = []
    user = current_user if current_user.is_authenticated() else None
    results = search_or_get_books(
        keyword,
        user,
        count=5,
        recursive=False
    )
    for book in results:
        books.append({
            'title': book['title'],
            'image': book['images']['small'],
            'douban_id': book['id'],
            'douban_url': book['url'],
            'author': ', '.join(book['author'])[:10],
            'url': ''
        })
    return jsonify(books)
