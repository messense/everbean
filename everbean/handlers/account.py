# coding=utf-8
from flask import Blueprint, render_template, \
    flash, url_for, session
from flask import request, redirect, current_app as app
from flask.ext.login import logout_user, \
    current_user, login_required
from everbean.core import db
from everbean.ext.douban import get_douban_client
from everbean.ext.evernote import get_evernote_client

bp = Blueprint('account', __name__, url_prefix='/account')


@bp.route('/login')
def login():
    """Redirect to douban.com to login"""
    if current_user.is_authenticated():
        return redirect(url_for('home.index'))
    client = get_douban_client()
    return redirect(client.authorize_url)


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
    if app.debug and app.config['EVERNOTE_SANDBOX'] and token:
        # using evernote sandox for development
        client = get_evernote_client(token=token)
        user_store = client.get_user_store()
        user = user_store.getUser()
        username = user.username

        #c_user = User.query.filter_by(id=current_user.id).first_or_404()
        current_user.evernote_username = username
        current_user.evernote_access_token = token
        current_user.is_i18n = True
        db.session.add(current_user)
        db.session.commit()

        flash(u'成功绑定 Evernote 账号 %s ！' % user.username, 'success')
        return redirect(url_for('home.index'))
    else:
        tp = request.args.get('type', '0')
        if tp == '0':
            return render_template('account/bind.html')

        is_i18n = True if tp == '1' else False
        session['is_i18n'] = is_i18n

        client = get_evernote_client(is_i18n)
        request_token = client.get_request_token(app.config['EVERNOTE_REDIRECT_URI'])
        session['evernote_oauth_token_secret'] = request_token['oauth_token_secret']
        return redirect(client.get_authorize_url(request_token))

