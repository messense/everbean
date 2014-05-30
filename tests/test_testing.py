# -*- coding: utf-8 -*-
import nose
from everbean.test import TestCase


class TestCaseTest(TestCase):
    def test_create_user(self):
        with self.app.app_context():
            user = self.create_user('test')
            self.assertIsNotNone(user.id)
            self.assertEqual(user.douban_name, 'test')
            self.assertEqual(user.douban_uid, 'test')

            user = self.create_user()
            self.assertIsNotNone(user.id)
            self.assertNotEqual(user.douban_name, 'test')
            self.assertEqual(user.douban_name, user.douban_uid)

    def test_login(self):
        with self.app.app_context():
            user = self.create_user()
            self.assertEqual(self.login(user), 'True')

if __name__ == '__main__':
    nose.runmodule()
