# coding=utf-8
from werkzeug.security import gen_salt
from flask import Blueprint, render_template
from flask import flash, url_for, session
from flask import request, redirect, current_app as app
from flask.ext.login import logout_user, current_user
from flask.ext.login import login_required
from flask.ext.mail import Message
from everbean.core import db, cache
from everbean.ext.douban import get_douban_client
from everbean.ext.evernote import get_evernote_client, get_notebooks
from everbean.forms import SettingsForm
from everbean.utils import to_unicode
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


@bp.route('/settings', methods=("GET", "POST"))
@login_required
def settings():
    @cache.memoize(300)
    def _get_notebooks(user):
        client = get_evernote_client(
            user.is_i18n,
            user.evernote_access_token
        )
        note_store = client.get_note_store()
        notebooks = []
        result = get_notebooks(note_store)
        for item in result:
            notebook = dict(
                guid=item.guid,
                name=to_unicode(item.name)
            )
            notebooks.append(notebook)
        return notebooks

    form = SettingsForm(obj=current_user)
    if current_user.evernote_access_token:
        _notebooks = _get_notebooks(current_user)
        form.evernote_notebook.choices = [(nb['guid'], nb['name'])
                                          for nb in _notebooks]
    if form.validate_on_submit():
        if form.email.data:
            current_user.email = form.email.data.strip().lower()
            current_user.email_verify_code = gen_salt(32)
            current_user.email_verified = False
            # send verification E-mail
            msg = Message(
                '[Everbean] 电子邮件验证',
                recipients=[current_user.email]
            )
            url = ''.join([
                app.config['SITE_URL'],
                url_for('account.verfify'),
                '?code=',
                current_user.email_verify_code
            ])
            msg.html = render_template('email/verify.html',
                                       user=current_user,
                                       url=url)
            tasks.send_mail.delay(msg)
            flash(u'一封含有电子邮件验证码的邮件已经发送到您的邮箱中，请点击其中的链接完成验证。', 'info')
        current_user.enable_sync = form.enable_sync.data
        current_user.evernote_notebook = form.evernote_notebook.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'帐号设置保存成功！', 'success')
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


@bp.route('/unbind')
@login_required
def unbind():
    if current_user.evernote_access_token:
        service_name = u'印象笔记'
        if current_user.is_i18n:
            service_name = u'Evernote'
        username = current_user.evernote_username
        current_user.evernote_username = ''
        current_user.evernote_access_token = ''
        db.session.add(current_user)
        db.session.commit()
        flash(u'已经解除本帐户与 %s 帐号 %s 的绑定。' % (service_name, username), 'success')
    return redirect(url_for('account.settings'))


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
