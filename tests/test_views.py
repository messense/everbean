# -*- coding: utf-8 -*-
import nose
from everbean.test import TestCase
from everbean.core import db


class AccountTest(TestCase):
    def test_db(self):
        with self.app.app_context():
            from everbean.models import User
            user = User()
            user.douban_uid = '1234'
            user.douban_id = 1234
            user.douban_name = 'test'
            user.douban_access_token = '12345678901234567890123456789012'
            user.douban_refresh_token = '12345678901234567890123456789012'
            db.session.add(user)
            db.session.commit()
            self.assertIsNotNone(user.id)

if __name__ == '__main__':
    nose.runmodule()
