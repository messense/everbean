# coding=utf-8
from __future__ import absolute_import, unicode_literals
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import ValidationError
from wtforms.fields import (
    TextField, TextAreaField,
    BooleanField, SelectField,
    IntegerField, HiddenField,
    RadioField,
)
from wtforms.validators import (
    Email, Optional,
    DataRequired, Length,
)
from everbean.models import User


class SettingsForm(Form):
    enable_sync = BooleanField('启用笔记同步')
    email = TextField('电子邮件', validators=[
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


class CreateNoteForm(Form):
    book_id = HiddenField('书籍 ID', default=0, validators=[
        DataRequired(message='必须提供书籍 ID 。')
    ])
    chapter = TextField('章节名', validators=[
        Optional(),
        Length(max=100, message='章节长度不能超过 100 字。')
    ])
    page_no = IntegerField('页 码', default=0, validators=[
        Optional()
    ])
    private = RadioField('隐 私', choices=[
        ('2', '所有人可见'),
        ('1', '仅自己可见')
    ], default='2')
    content = TextAreaField('笔记内容', validators=[
        DataRequired(message='笔记内容不能为空。'),
        Length(min=16, message='笔记内容长度必须大于 15 字。')
    ])


class EditNoteForm(Form):
    chapter = TextField('章节名', validators=[
        Optional(),
        Length(max=100, message='章节长度不能超过 100 字。')
    ])
    page_no = IntegerField('页 码', default=0, validators=[
        Optional()
    ])
    private = RadioField('隐 私', choices=[
        ('2', '所有人可见'),
        ('1', '仅自己可见')
    ], default='2')
    content = TextAreaField('笔记内容', validators=[
        DataRequired(message='笔记内容不能为空。'),
        Length(min=16, message='笔记内容长度必须大于 15 字。')
    ])
