Everbean
===========
Sync notes from book.douban.com to Evernote

[![Build Status](https://travis-ci.org/messense/everbean.svg?branch=develop)](https://travis-ci.org/messense/everbean)
[![Coverage Status](https://coveralls.io/repos/messense/everbean/badge.png)](https://coveralls.io/r/messense/everbean)

## Installation

1. Clone or download this repository to your local disk and change directory to that directory.
2. Install dependencies using pip:

        pip install -r requirements.txt
        # install optional dependencies if you want a better performance
        pip install -r optional-requirements.txt

3. Now you are good to go

## Configuration

Copy `config-sample.py` or rename it to `config.py`, then make the changes as you wish.

## Database creation

Run `python manage.py syncdb` to automatically create database structure for the first time.

## Database migration

Run

    python manage.py db upgrade
    python manage.py syncdb

to migrate database to the latest version.

## Clear cache

Run `python manage.py clear_cache` to clear any existing caches in memcached.

## Start a server for development

Run `python manage.py runserver` to start a local server for development.

## Start Celery worker

Run `celery worker --app=celeryworker.app -l info` to start Celery woker process.

## Deployment

Check out [conf](conf/) directory for `nginx.conf`, `supervisor.conf` and `crontab` configuration.

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
