#!/usr/local/bin python
# coding=utf-8
from __future__ import with_statement
from everbean.app import create_app
from everbean.core import celery


app = create_app()

TaskBase = celery.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

celery.Task = ContextTask
