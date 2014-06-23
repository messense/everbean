# coding=utf-8
from __future__ import absolute_import, unicode_literals
from flask import Blueprint, jsonify
from everbean.models import Book


bp = Blueprint('api', __name__, url_prefix='/api')

