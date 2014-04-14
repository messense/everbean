# coding=utf-8
from flask import Blueprint, render_template, \
    flash, url_for, session
from flask import request, redirect, current_app as app
from flask.ext.login import logout_user, \
    current_user, login_required
from werkzeug.security import gen_salt
from everbean.core import db
from everbean.ext.douban import get_douban_client
from everbean.ext.evernote import get_evernote_client, get_notebooks
from everbean.forms import SettingsForm
from everbean.utils import ObjectDict, to_unicode
from everbean.models import User
import everbean.tasks as tasks

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
    def _get_notebooks(is_i18n, token):
        client = get_evernote_client(is_i18n, token)
        note_store = client.get_note_store()
        notebooks = []
        result = get_notebooks(note_store)
        for item in result:
            notebook = ObjectDict(
                guid=item.guid,
                name=to_unicode(item.name)
            )
            notebooks.append(notebook)
        return notebooks

    form = SettingsForm(obj=current_user)
    if current_user.evernote_access_token:
        if 'evernote_notebooks' in session:
            _notebooks = session['evernote_notebooks']
        else:
            _notebooks = _get_notebooks(current_user.is_i18n,
                                        current_user.evernote_access_token)
            session['evernote_notebooks'] = _notebooks
        form.evernote_notebook.choices = [(nb['guid'], nb['name'])
                                          for nb in _notebooks]
    if form.validate_on_submit():
        if form.email.data:
            current_user.email = form.email.data
            current_user.email_verify_code = gen_salt(32)
            current_user.email_verified = False
            # Todo: send verification E-mail
            
            flash(u'一封含有电子邮件验证码的邮件已经发送到您的邮箱中，请点击其中的链接完成验证。', 'info')
        current_user.enable_sync = form.enable_sync.data
        current_user.evernote_notebook = form.evernote_notebook.data
        db.session.add(current_user)
        db.session.commit()
    return render_template('account/settings.html', form=form)


@bp.route('/bind')
@login_required
def bind():
    sandbox_token = app.config['EVERNOTE_SANDBOX_TOKEN']
    if app.debug and app.config['EVERNOTE_SANDBOX'] and sandbox_token:
        # using evernote sandox for development
        client = get_evernote_client(token=sandbox_token)
        user_store = client.get_user_store()
        user = user_store.getUser()
        username = user.username

        # c_user = User.query.filter_by(id=current_user.id).first_or_404()
        current_user.evernote_username = username
        current_user.evernote_access_token = sandbox_token
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
        token = client.get_request_token(app.config['EVERNOTE_REDIRECT_URI'])
        session['evernote_oauth_token_secret'] = token['oauth_token_secret']
        return redirect(client.get_authorize_url(token))


@bp.route('/verify')
def verify():
    code = request.args.get('code', '')
    if not code:
        flash(u'没有有效的电子邮件验证码！', 'error')
        return redirect(url_for('home.index'))
    user = User.query.filter_by(email_verify_code=code).first()
    if not user:
        flash(u'无效的电子邮件验证码！', 'error')
        return redirect(url_for('home.index'))
    if user.email_verified:
        flash(u'此电子邮件已经验证通过！', 'info')
        return redirect(url_for('home.index'))
    user.email_verified = True
    db.session.add(user)
    db.session.commit()

    flash(u'电子邮件激活成功！', 'success')
    return redirect(url_for('home.index'))
