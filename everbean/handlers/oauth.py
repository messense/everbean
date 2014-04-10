# coding=utf-8
from datetime import datetime
from flask import Blueprint, flash, url_for, session
from flask import request, redirect, current_app as app
from flask.ext.login import current_user, login_required, login_user
from everbean.core import db
from everbean.models import User
from everbean.ext.douban import get_douban_client
from everbean.ext.evernote import get_evernote_client
from everbean import tasks

bp = Blueprint('oauth', __name__, url_prefix='/oauth')


@bp.route('/douban')
def douban():
    """Use request argument code to get OAuth2
    access_token, refresh_token and etc."""
    if current_user.is_authenticated():
        return redirect(url_for('home.index'))
    error = request.args.get('error', '')
    code = request.args.get('code', '')
    if error or (not code):
        app.logger.warning('Error happened: %s' % error)
        flash(u'豆瓣 OAuth 登录失败！', 'error')
        return redirect(url_for('home.index'))

    client = get_douban_client()
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

    # sync books to database for the first time
    tasks.sync_books.delay(user)
    tasks.import_douban_annotations.delay(user)

    return redirect(url_for('home.index'))


@bp.route('/evernote')
@login_required
def evernote():
    is_i18n = bool(session['is_i18n'])
    client = get_evernote_client(is_i18n)
    oauth_token = request.args.get('oauth_token')
    oauth_token_secret = session['evernote_oauth_token_secret']
    oauth_verifier = request.args.get('oauth_verifier')

    if not (oauth_token and oauth_token_secret and oauth_verifier):
        flash(u'绑定 Evernote 失败！', 'error')
        return redirect(url_for('account.bind'))

    auth_token = client.get_access_token(oauth_token,
                                         oauth_token_secret,
                                         oauth_verifier)
    app.logger.debug('evernote auth_token: %s' % auth_token)

    if auth_token:
        client = get_evernote_client(token=auth_token)
        user_store = client.get_user_store()
        user = user_store.getUser()

        current_user.evernote_username = user.username
        current_user.evernote_access_token = auth_token
        current_user.is_i18n = is_i18n
        db.session.add(current_user)
        db.session.commit()

        # sync notes for the first time
        c_user = User.query.filter_by(id=current_user.id).first()
        tasks.sync_notes(c_user)
        if is_i18n:
            flash(u'成功绑定 Evernote 账号 %s ！' % user.username, 'success')
        else:
            flash(u'成功绑定 印象笔记 账号 %s ！' % user.username, 'success')
        return redirect(url_for('home.index'))
    else:
        if is_i18n:
            flash(u'绑定 Evernote 失败！', 'error')
        else:
            flash(u'绑定 印象笔记 失败！', 'error')
        return redirect(url_for('account.bind'))