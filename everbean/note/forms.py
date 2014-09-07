# coding=utf-8
from __future__ import absolute_import, unicode_literals

from flask.ext.wtf import Form
from wtforms.fields import (
    StringField, TextAreaField,
    IntegerField, HiddenField,
    RadioField,
)
from wtforms.validators import Optional, DataRequired, Length


class CreateNoteForm(Form):
    book_id = HiddenField('书籍 ID', default=0, validators=[
        DataRequired(message='必须提供书籍 ID 。')
    ])
    chapter = StringField('章节名', validators=[
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
    chapter = StringField('章节名', validators=[
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
