# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, with_statement
import nose
from flask import url_for
from werkzeug.security import gen_salt
from everbean.test import TestCase
from everbean.core import db
from everbean.models import User


class AccountTest(TestCase):
    def test_login_get(self):
        with self.app.app_context():
            response = self.client.get(url_for('account.login'))
            self.assertEqual(response.status_code, 302)

    def test_settings_get(self):
        with self.app.app_context():
            response = self.client.get(url_for('account.settings'))
            self.assertEqual(response.status_code, 302)

            user = self.create_user('test')
            self.login(user)
            response = self.client.get(url_for('account.settings'))
            self.assertEqual(response.status_code, 200)

    def test_verify(self):
        with self.app.app_context():
            response = self.client.get(url_for('account.verify', code='12345'))
            self.assertEqual(response.status_code, 302)

            user = self.create_user('test')
            user.email = 'test@test.com'
            user.email_verify_code = gen_salt(32)
            user.email_verified = False
            db.session.add(user)
            db.session.commit()

            self.client.get(url_for('account.verify', code='12345'))
            user = User.query.get(user.id)
            self.assertFalse(user.email_verified)

            self.client.get(url_for('account.verify', code=user.email_verify_code))
            user = User.query.get(user.id)
            self.assertTrue(user.email_verified)

if __name__ == '__main__':
    nose.runmodule()
