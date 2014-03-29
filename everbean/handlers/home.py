# coding=utf-8
from flask import Blueprint, render_template

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/')
def index():
    return render_template('home/index.html')

@bp.route('about')
def about():
    return render_template('home/about.html')

@bp.route('faq')
def faq():
    return render_template('home/faq.html')
