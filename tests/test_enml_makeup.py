# coding=utf-8
from __future__ import absolute_import, with_statement, unicode_literals
import os
from datetime import datetime

import nose

from everbean.app import create_app
from everbean.ext.evernote import generate_enml_makeup, enml_to_html
from everbean.utils import ObjectDict


def _create_book_notes():
    created = datetime(2014, 4, 1, 0, 0, 0)
    book = ObjectDict(
        title='Test',
        author='messense',
        alt='http://www.douban.com'
    )

    notes = [
        ObjectDict(
            chapter='Chapter 1',
            page_no=0,
            alt='http://www.douban.com',
            content='<blockquote><q>This is a quote.</q></blockquote>Test 1',
            created=created
        ),
        ObjectDict(
            chapter='Chapter 1',
            page_no=0,
            alt='http://www.douban.com',
            content='<blockquote><q>This is a quote.</q></blockquote>Test 2',
            created=created
        ),
        ObjectDict(
            chapter='Chapter 2',
            page_no=0,
            alt='http://www.douban.com',
            content='<blockquote><q>This is a quote.</q></blockquote>Test',
            created=created
        ),
        ObjectDict(
            chapter='',
            page_no=0,
            alt='http://www.douban.com',
            content='<blockquote><q>This is a quote.</q></blockquote>Test',
            created=created
        ),
    ]

    book.notes = notes
    return book, notes


def test_enml_makeup():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, 'config.py')

    book, notes = _create_book_notes()

    app = create_app(config_file)
    with app.app_context():
        makeup = generate_enml_makeup(book, notes)
        assert '<en-note>' in makeup
        assert '</en-note>' in makeup
        assert '<h2 style="font-size:18pt; text-align:right;">' \
               '{title}</h2>'.format(title=book.title) in makeup
        assert '<h5 style="font-size:12pt; text-align:right; color:gray;">' \
               '{author}</h5>'.format(author=book.author) in makeup
        assert '__DEFAULT__' not in makeup
        assert '<span style="font-weight:bold; background-color:white;' \
               'position:relative;">Chapter 1</span>' in makeup
        assert '<a href="http://www.douban.com" ' \
               'style="text-decoration:none">' in makeup


def test_enml_to_html():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, 'config.py')

    book, notes = _create_book_notes()

    app = create_app(config_file)
    with app.app_context():
        makeup = generate_enml_makeup(book, notes)
        html = enml_to_html(makeup)
        print(html)
        assert '<en-note>' not in html
        assert '</en-note>' not in html
        assert 'http://xml.evernote.com/pub/enml2.dtd' not in html


if __name__ == '__main__':
    nose.runmodule()
