Everbean
===========

Sync notes from book.douban.com to Evernote

[![Build Status](https://travis-ci.org/messense/everbean.svg?branch=develop)](https://travis-ci.org/messense/everbean)

## Installation

* Install dependencies with pip:

    pip install -U -r requirements.txt

* Install optional dependencies with pip if you want a better performance:

    pip install -U -r optional-requirements.txt

* Copy config-sample.py to config.py and apply your modification, then set environment var `everbean_config` to the path of config.py:

    export everbean_config=/path/to/your/config.py

* Now we can start the server:

    python wsgi.py

Or:

    python manage.py runserver

## Database creation

run `python manage.py syncdb` to automatically create database structure for the first time.

## Database migration

run `python manage.py db upgrade` to migrate database to the latest version.

## License

The MIT License (MIT)

Copyright (c) 2014 messense

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
