# coding=utf-8
from datetime import datetime
from flask import Blueprint, render_template, abort
from flask import request, redirect, current_app as app
from jinja2 import TemplateNotFound

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/')
def index():
    return 'index page'
