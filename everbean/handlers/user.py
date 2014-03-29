# coding=utf-8
from flask import Blueprint, render_template, abort
from flask.ext.login import current_user, login_required
from everbean.models import User

bp = Blueprint('user', __name__, url_prefix='/u')

@bp.route('/<uid>')
@login_required
def index(uid=None):
    user = None
    if uid is None or current_user.douban_uid == uid:
        user = current_user
    else:
        user = User.query.filter_by(douban_uid=uid).first()
        if not user:
            abort(404)
    return render_template('user/index.html', user=user)
