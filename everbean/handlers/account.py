# coding=utf-8
from datetime import datetime
from flask import Blueprint, render_template, \
    flash, url_for, session
from flask import request, redirect, current_app as app
from flask.ext.login import login_user, logout_user, \
    current_user, login_required
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
    if not app.debug and app.config['EVERNOTE_SANDBOX'] and token:
        # using evernote sandox for development
        client = EvernoteClient(token=token)
        user_store = client.get_user_store()
        user = user_store.getUser()
        username = user.username

        #c_user = User.query.filter_by(id=current_user.id).first_or_404()
        current_user.evernote_username = username
        current_user.evernote_access_token = token
        db.session.add(current_user)
        db.session.commit()
        flash(u'成功绑定 Evernote 账号 %s ！' % user.username, 'success')
        return redirect(url_for('home.index'))
    else:
        tp = request.args.get('type', '0')
        is_i18n = True if tp == '1' else False
        if is_i18n:
            client = EvernoteClient(consumer_key=app.config['EVERNOTE_CONSUMER_KEY'],
                                    consumer_secret=app.config['EVERNOTE_CONSUMER_SECRET'],
                                    sandbox=app.config['EVERNOTE_SANDBOX'])
            request_token = client.get_request_token(app.config['EVERNOTE_REDIRECT_URI'])
            session['evernote_oauth_token_secret'] = request_token['oauth_token_secret']
            return redirect(client.get_authorize_url(request_token))
        else:
            pass
        if tp == '0':
            return render_template('account/bind.html')

@bp.route('/evernote')
@login_required
def evernote():
    client = EvernoteClient(consumer_key=app.config['EVERNOTE_CONSUMER_KEY'],
                            consumer_secret=app.config['EVERNOTE_CONSUMER_SECRET'],
                            sandbox=app.config['EVERNOTE_SANDBOX'])
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
        client = EvernoteClient(token=auth_token)
        user_store = client.get_user_store()
        user = user_store.getUser()

        current_user.evernote_username = user.username
        current_user.evernote_access_token = auth_token
        db.session.add(current_user)
        db.session.commit()
        flash(u'成功绑定 Evernote 账号 %s ！' % user.username, 'success')
        return redirect(url_for('home.index'))
    else:
        flash(u'绑定 Evernote 失败！', 'error')
        return redirect(url_for('account.bind'))


@bp.route('/yinxiang')
@login_required
def yinxiang():
    pass