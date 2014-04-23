#!/usr/local/bin python
# coding=utf-8
from __future__ import with_statement
from everbean.app import create_app
from everbean.core import celery as app


flask = create_app()

TaskBase = app.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with flask.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

app.Task = ContextTask
