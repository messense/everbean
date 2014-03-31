#!/usr/bin/env python
# coding=utf-8
import time
from everbean.app import create_app
from everbean.models import User
from everbean import tasks


def main():
    app = create_app()

    # refresh access token one day before access token expires
    expires_time = int(time.time()) - 86400
    users = User.query.filter_by(enable_sync=True, douban_expires_at__lte=expires_time).all()
    refresh_access_token(app, users)

    users = User.query.filter_by(enable_sync=True).all()
    sync_books(app, users)

    users = User.query.filter_by(enable_sync=True, evernote_username__isnull=False).all()
    sync_notes(app, users)


def refresh_access_token(app, users):
    with app.app_context():
        for user in users:
            tasks.refresh_douban_access_token(user)


def sync_books(app, users):
    with app.app_context():
        for user in users:
            tasks.sync_books.delay(user)


def sync_notes(app, users):
    with app.app_context():
        for user in users:
            tasks.sync_notes.delay(user)


if __name__ == '__main__':
    main()