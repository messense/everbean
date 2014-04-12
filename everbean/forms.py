# coding=utf-8
from flask.ext.wtf import Form
from wtforms.fields import TextField, TextAreaField, Label, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Optional


class SettingsForm(Form):
    pass
