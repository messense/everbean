# coding=utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from flask import Blueprint, flash, url_for, session
from flask import request, redirect, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.login import login_user
from douban_client.api.error import DoubanAPIError

from ..core import db, cache
from ..account.models import User
from ..ext.douban import get_douban_client
from ..ext.evernote import get_evernote_client
from .. import tasks


blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')


@blueprint.route('/douban')
def douban():
    """Use request argument code to get OAuth2
    access_token, refresh_token and etc."""
    if current_user.is_authenticated():
        return redirect(url_for('home.index'))
    error = request.args.get('error', '')
    code = request.args.get('code', '')
    if error or (not code):
        app.logger.warning('Error happened: %s', error)
        flash('豆瓣 OAuth 登录失败！', 'error')
        return redirect(url_for('home.index'))

    client = get_douban_client()
    client.auth_with_code(code)

    try:
        me = client.user.me
    except DoubanAPIError as e:
        app.logger.error('Error happened: status(%s), reason(%s)', e.status, e.reason)
        flash('豆瓣 OAuth 登录失败！', 'error')
        return redirect(url_for('home.index'))

    user = User.query.filter_by(douban_id=me['id']).first()
    is_new_user = False
    if user is None:
        is_new_user = True
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
    tasks.sync_books.delay(user.id)
    if is_new_user:
        tasks.import_douban_annotations.delay(user.id)

    # clear cache
    cache.clear()

    return redirect(url_for('home.index'))


@blueprint.route('/evernote')
@login_required
def evernote():
    is_i18n = bool(session['is_i18n'])
    client = get_evernote_client(is_i18n)
    oauth_token = request.args.get('oauth_token')
    oauth_token_secret = session['evernote_oauth_token_secret']
    oauth_verifier = request.args.get('oauth_verifier')

    if not (oauth_token and oauth_token_secret and oauth_verifier):
        flash('绑定 Evernote 失败！', 'error')
        return redirect(url_for('account.bind'))

    auth_token = client.get_access_token(
        oauth_token,
        oauth_token_secret,
        oauth_verifier
    )

    if auth_token:
        client = get_evernote_client(is_i18n, auth_token)
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
            flash('成功绑定 Evernote 账号 {name} ！'.format(name=user.username), 'success')
        else:
            flash('成功绑定 印象笔记 账号 {name} ！'.format(name=user.username), 'success')
        return redirect(url_for('home.index'))
    else:
        if is_i18n:
            flash('绑定 Evernote 失败！', 'error')
        else:
            flash('绑定 印象笔记 失败！', 'error')
        return redirect(url_for('account.bind'))
