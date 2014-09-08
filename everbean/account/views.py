# coding=utf-8
from __future__ import absolute_import, unicode_literals

from werkzeug.security import gen_salt
from flask import Blueprint, render_template
from flask import flash, url_for, session, abort
from flask import request, redirect, current_app as app
from flask.ext.login import logout_user, current_user, login_user
from flask.ext.login import login_required
from flask.ext.mail import Message

from ..core import db, cache
from ..ext.douban import get_douban_client
from ..ext.evernote import get_evernote_client, get_notebooks
from ..utils import to_text
from .. import tasks

from .models import User
from .forms import SettingsForm


blueprint = Blueprint('account', __name__, url_prefix='/account')


@blueprint.route('/login')
def login():
    """Redirect to douban.com to login"""
    if current_user.is_authenticated():
        return redirect(url_for('home.index'))
    client = get_douban_client()
    return redirect(client.authorize_url)


@blueprint.route('/fakelogin', methods=('POST', ))
def fakelogin():
    if not app.config['TESTING']:
        abort(403)
    username = request.form.get('username', None)
    if username:
        user = User.query.filter_by(douban_uid=username).first()
        if user:
            login_user(user, remember=True)
            return 'True'
    return 'False'


@blueprint.route('/logout')
def logout():
    """logout user"""
    if current_user.is_authenticated():
        logout_user()
    return redirect(url_for('home.index'))


@blueprint.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    from ..ext.evernote import get_available_templates

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
                name=to_text(item.name)
            )
            notebooks.append(notebook)
        return notebooks

    def send_verification_mail(user):
        msg = Message(
            sender=app.config['DEFAULT_MAIL_SENDER'],
            subject='[Everbean] 电子邮件验证',
            recipients=[user.email, ]
        )
        url = ''.join([
            app.config['SITE_URL'],
            url_for('account.verify', code=user.email_verify_code),
        ])
        msg.html = render_template('email/verify.html',
                                   user=user,
                                   url=url)
        tasks.send_mail.delay(msg)
        flash('一封含有电子邮件验证码的邮件已经发送到您的邮箱中，请点击其中的链接完成验证。', 'info')

    if current_user.email and not current_user.email_verified:
        resend = request.args.get('resend', False)
        if resend:
            send_verification_mail(current_user)
        else:
            flash('您的电子邮件地址尚未验证，请查看您的邮箱并点击其中的链接完成验证。'
                  '没有收到验证邮件？请点击<a href="?resend=true">这里</a>重新发送验证邮件。', 'warning')

    form = SettingsForm(obj=current_user)
    form.template.choices = get_available_templates()
    if current_user.evernote_access_token:
        _notebooks = _get_notebooks(current_user)
        form.evernote_notebook.choices = [(nb['guid'], nb['name'])
                                          for nb in _notebooks]
    else:
        form.evernote_notebook.choices = []
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if email and current_user.email != email:
            # current user has no email or change email
            current_user.email = email
            current_user.email_verify_code = gen_salt(32)
            current_user.email_verified = False
            # send verification E-mail
            send_verification_mail(current_user)
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash('帐号设置保存成功！', 'success')
    return render_template('account/settings.html', form=form)


@blueprint.route('/bind')
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

        flash('成功绑定 Evernote 账号 {name} ！'.format(name=user.username), 'success')
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


@blueprint.route('/unbind')
@login_required
def unbind():
    if current_user.evernote_access_token:
        service_name = '印象笔记'
        if current_user.is_i18n:
            service_name = 'Evernote'
        username = current_user.evernote_username
        current_user.evernote_username = ''
        current_user.evernote_access_token = ''
        db.session.add(current_user)
        db.session.commit()
        flash('已经解除本帐户与 {service} 帐号 {name} 的绑定。'.format(
            service=service_name,
            name=username
        ), 'success')
    return redirect(url_for('account.settings'))


@blueprint.route('/verify/<code>')
def verify(code):
    if not code:
        flash('没有有效的电子邮件验证码！', 'error')
        return redirect(url_for('home.index'))
    user = User.query.filter_by(email_verify_code=code).first()
    if not user:
        flash('无效的电子邮件验证码！', 'error')
        return redirect(url_for('home.index'))
    if user.email_verified:
        flash('此电子邮件已经验证通过！', 'info')
        return redirect(url_for('home.index'))
    user.email_verified = True
    db.session.add(user)
    db.session.commit()

    flash('电子邮件激活成功！', 'success')
    return redirect(url_for('home.index'))
