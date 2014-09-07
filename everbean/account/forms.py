# coding=utf-8
from __future__ import absolute_import, unicode_literals

from wtforms import ValidationError
from wtforms.fields import StringField, BooleanField, SelectField
from wtforms.validators import Email, Optional
from flask.ext.wtf import Form
from flask.ext.login import current_user

from everbean.account.models import User


class SettingsForm(Form):
    enable_sync = BooleanField('启用笔记同步')
    email = StringField('电子邮件', validators=[
        Email(message='请输入有效的 Email 地址。'),
        Optional(),
    ])
    evernote_notebook = SelectField('默认笔记本', validators=[
        Optional(),
    ])
    template = SelectField('笔记模板', choices=[
        ('default', 'Default'),
    ], default='default')

    def validate_email(self, field):
        mail = field.data.strip().lower()
        user = User.query.filter_by(email=mail).first()
        if user and user.id != current_user.id:
            raise ValidationError('这个电子邮件地址已经被使用过了。')
