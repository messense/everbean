# coding=utf-8
from flask.ext.wtf import Form
from wtforms.fields import TextField, BooleanField, SelectField
from wtforms.validators import Email, Optional


class SettingsForm(Form):
    enable_sync = BooleanField(u'启用笔记同步')
    email = TextField(u'电子邮件', validators=[
        Email(),
        Optional(),
    ])
    evernote_notebook = SelectField(u'默认笔记本', validators=[
        Optional(),
    ])
