#!/usr/bin/env python
# coding=utf-8
from everbean.app import create_app
from everbean.models import User
from everbean import tasks

def main():
    app = create_app()
    users = User.query.filter_by(enable_sync=True)

    sync_books(app, users)
    sync_notes(app, users)


def sync_books(app, users):
    for user in users:
        tasks.sync_books.delay(user)


def sync_notes(app, users):
    for user in users:
        tasks.sync_notes.delay(user)


if __name__ == '__main__':
    main()