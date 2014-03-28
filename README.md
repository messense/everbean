Everbean
===========

Sync notes from book.douban.com to Evernote

## Installation

* Install dependencies with pip:

    pip install -U -r requirements.txt

* Install optional dependencies with pip if you want a better performance:

    pip install -U -r optional-requirements.txt

* Copy config-sample.py as config.py and apply your modification, then set environment var `everbean_config` to the path of config.py:

    export everbean_config=/path/to/your/config.py

* Now we can start the server:

    python wsgi.py

## Database creation

run `python manage.py create_db` to automatically create database structure for the first time.

## Database migration

run `python manage.py db migrate` to migrate database to the latest version.
