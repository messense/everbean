# coding=utf-8
from datetime import datetime
from flask import Blueprint, render_template, abort, url_for
from flask import request, redirect, current_app as app
from flask.ext.login import login_user, logout_user, current_user, login_required
from douban_client import DoubanClient
from evernote.api.client import EvernoteClient
from everbean.core import db
from everbean.models import User

bp = Blueprint('account', __name__, url_prefix='/account')


@bp.route('/login')
def login():
    """Redirect to douban.com to login"""
    if current_user.is_authenticated():
        return redirect(url_for('home.index'))
    client = DoubanClient(app.config['DOUBAN_API_KEY'],
                          app.config['DOUBAN_API_SECRET'],
                          app.config['DOUBAN_REDIRECT_URI'],
                          app.config['DOUBAN_API_SCOPE'])
    return redirect(client.authorize_url)


@bp.route('/douban')
def login_with_douban():
    """Use request argument code to get OAuth2
    access_token, refresh_token and etc."""
    if current_user.is_authenticated():
        return redirect(url_for('home.index'))
    error = request.args.get('error', '')
    code = request.args.get('code', '')
    if error or (not code):
        app.logger.warning('Error happened: %s' % error)
        return render_template('account/login_error.html', errmsg="OAuth 授权出错！")

    client = DoubanClient(app.config['DOUBAN_API_KEY'],
                          app.config['DOUBAN_API_SECRET'],
                          app.config['DOUBAN_REDIRECT_URI'],
                          app.config['DOUBAN_API_SCOPE'])
    client.auth_with_code(code)

    me = client.user.me

    user = User.query.filter_by(douban_id=me['id']).first()
    if user is None:
        # register user
        user = User()
        user.created = datetime.now()
        user.douban_id = me['id']
        user.douban_uid = me['uid']
        user.douban_alt = me['alt']
    # update user infomation
    user.douban_access_token = client.token_code
    user.douban_refresh_token = client.refresh_token_code
    user.douban_expires_at = client.access_token.expires_at
    user.douban_name = me['name']
    user.avatar = me['avatar']
    user.large_avatar = me['avatar'].replace('icon/u', 'icon/ul')
    user.signature = me['signature']
    user.desc = me['desc']

    db.session.add(user)
    db.session.commit()

    login_user(user, remember=True)

    return redirect(url_for('home.index'))


@bp.route('/logout')
def logout():
    """logout user"""
    if current_user.is_authenticated():
        logout_user()
    return redirect(url_for('home.index'))

@bp.route('/settings')
@login_required
def settings():
    return render_template('account/settings.html')


@bp.route('/bind')
@login_required
def bind():
    token = app.config['EVERNOTE_SANDBOX_TOKEN']
    if app.config['EVERNOTE_SANDBOX'] and token:
        # using evernote sandox for development
        client = EvernoteClient(token=token)
        user_store = client.get_user_store()
        user = user_store.getUser()
        username = user.username

        c_user = User.query.filter_by(id=current_user.id).first_or_404()
        c_user.evernote_username = username
        c_user.evernote_access_token = token
        db.session.add(c_user)
        db.session.commit()
        return redirect(url_for('home.index'))
    else:
        tp = request.args.get('type', '0')
        is_i18n = True if tp == '1' else False
        if is_i18n:
            pass
        else:
            pass
        if tp == '0':
            return render_template('account/bind.html')

@bp.route('/evernote')
@login_required
def evernote():
    pass

@bp.route('/yinxiang')
@login_required
def yinxiang():
    pass