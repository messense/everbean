# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, with_statement
import os
import random
import unittest
import tempfile
from werkzeug.security import gen_salt
from flask import url_for
from everbean.app import create_app
from everbean.core import db
from everbean.models import User


class TestCase(unittest.TestCase):

    __config__ = None

    def setUp(self):
        if hasattr(self, 'pre_setUp'):
            self.pre_setUp()
        super(TestCase, self).setUp()

    def tearDown(self):
        if hasattr(self, 'pre_tearDown'):
            self.pre_tearDown()
        super(TestCase, self).tearDown()

    def pre_setUp(self):
        if self.__config__ is None:
            config = {
                'SECRET_KEY': 'testing',
                'DOUBAN_API_KEY': '',
                'DOUBAN_API_SECRET': '',
                'DOUBAN_REDIRECT_URI': '',
                'EVERNOTE_CONSUMER_KEY': '',
                'EVERNOTE_CONSUMER_SECRET': '',
            }
            self.db_fd, self.db_path = tempfile.mkstemp('.db')
            config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{path}'.format(path=self.db_path)
        else:
            config = self.__config__
        self.app = create_app(config, debug=True)
        self.app.config['TESTING'] = True
        self.app.config['SERVER_NAME'] = 'localhost'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def pre_tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def login(self, user):
        return self.client.post(url_for('account.fakelogin'), data={
            'username': user.douban_uid,
        }).data

    def logout(self):
        self.client.get(url_for('account.logout'))

    def create_user(self, username=None):
        username = username or gen_salt(6)
        user = User()
        user.douban_uid = username
        user.douban_name = username
        user.douban_id = random.randint(1, 1000)
        user.douban_access_token = gen_salt(32)
        user.douban_refresh_token = gen_salt(32)
        db.session.add(user)
        db.session.commit()
        return user
