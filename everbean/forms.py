# coding=utf-8
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
    enable_sync = BooleanField(u'启用笔记同步')
    email = TextField(u'电子邮件', validators=[
        Email(),
        Optional(),
    ])
    evernote_notebook = SelectField(u'默认笔记本', validators=[
        Optional(),
    ])

    def validate_email(self, field):
        mail = field.data.strip().lower()
        user = User.query.filter_by(email=mail).first()
        if user and user.id != current_user.id:
            raise ValidationError('这个电子邮件地址已经被使用过了。')


class CreateNoteForm(Form):
    book_id = HiddenField(u'书籍 ID', default=0, validators=[
        DataRequired()
    ])
    chapter = TextField(u'章节名', validators=[
        Optional(),
        Length(max=100, message=u'章节长度不能超过 100 字。')
    ])
    page_no = IntegerField(u'页 码', default=0, validators=[
        Optional()
    ])
    private = RadioField(u'隐 私', choices=[
        (2, u'所有人可见'),
        (1, u'仅自己可见')
    ], default=2)
    content = TextAreaField(u'笔记内容', validators=[
        DataRequired(),
        Length(min=16, message=u'笔记内容长度必须大于 15 字。')
    ])

    def validate_chapter_and_page(self):
        if not (self.chapter or self.page_no > 0):
            raise ValidationError('章节和页数必须填写其中一个！')
        if self.chapter and self.page_no > 0:
            raise ValidationError('章节和页数只能填写其中一个！')
        if self.page_no > 0 and len(str(self.page_no)) > 6:
            raise ValidationError('页数不能超过 6 位数字。')
