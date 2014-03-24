Everbean
===========

Sync notes from book.douban.com to Evernote

## Installation

* Install dependencies with pip:

    pip install -r requirements.txt

* Copy config-sample.py as config.py and apply your modification, then set environment var `everbean_config` to the path of config.py:

    export everbean_config=/path/to/your/config.py

* Now we can start the server:

    python wsgi.py
