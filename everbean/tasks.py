# coding=utf-8
from flask import current_app as app
from flask.ext.mail import Message
from everbean.app import create_celery_app
from everbean.core import mail

celery = create_celery_app(app)

@celery.task
def send_mail(messages):
    if isinstance(messages, Message):
        messages = [messages, ]
    with mail.connect() as conn:
        for msg in messages:
            conn.send(msg)


@celery.task
def sync_books(user):
    pass


@celery.task
def find_books(user):
    pass


@celery.task
def sync_notes(user, book):
    pass