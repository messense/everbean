# coding=utf-8
from __future__ import absolute_import, unicode_literals
import json
from flask import Blueprint, jsonify as flask_jsonify
from flask import request, Response
from flask.ext.login import current_user, login_required
from everbean.models import Book
from everbean.ext.douban import search_or_get_books


bp = Blueprint('api', __name__, url_prefix='/api')


def jsonify(*args, **kwargs):
    if args and len(args) == 1 and not kwargs:
        s = json.dumps(args[0])
        return Response(s, mimetype='application/json')
    else:
        return flask_jsonify(*args, **kwargs)


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
        count=10,
        recursive=False
    )
    for book in results:
        books.append({
            'title': book['title'],
            'image': book['images']['small'],
            'douban_id': book['id'],
            'douban_url': book['url'],
        })
    return jsonify(books)
