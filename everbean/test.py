# -*- coding: utf-8 -*-
import os
import unittest
import tempfile
from everbean.app import create_app
from everbean.core import db


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
            config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.db_path
        else:
            config = self.__config__
        self.app = create_app(config, debug=True)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def pre_tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
