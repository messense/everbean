# coding=utf-8
from __future__ import absolute_import, with_statement, unicode_literals
import os
import nose
from datetime import datetime
from everbean.app import create_app
from everbean.ext.evernote import generate_enml_makeup
from everbean.utils import ObjectDict


def test_enml_makeup():
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

    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, 'config.py')

    app = create_app(config_file)
    with app.app_context():
        makeup = generate_enml_makeup(book, notes)
        assert '<h2 style="font-size:18pt; text-align:right;">%s</h2>' % \
               book.title in makeup
        assert '<h5 style="font-size:12pt; text-align:right; color:gray;">%s</h5>' % \
               book.author in makeup
        assert '__DEFAULT__' not in makeup
        assert '<span style="font-weight:bold; background-color:white;' \
               'position:relative;">Chapter 1</span>' in makeup
        assert '<a href="http://www.douban.com" ' \
               'style="text-decoration:none">' in makeup


if __name__ == '__main__':
    nose.runmodule()
