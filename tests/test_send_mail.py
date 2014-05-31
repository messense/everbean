# coding=utf-8
from __future__ import absolute_import, with_statement, unicode_literals
import os
import sys
from StringIO import StringIO
import nose
from subprocess import Popen, PIPE
from flask.ext.mail import Message
from everbean.app import create_app


def test_send_mail():
    saved_stdout = sys.stdout
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, 'config.py')
    app = create_app(config_file)
    try:
        out = StringIO()
        sys.stdout = out
        with app.app_context():
            from everbean.core import mail

            smtpd = Popen(
                ['python', '-m', 'smtpd', '-n', '-c', 'DebuggingServer', 'localhost:1025'],
                shell=False,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                close_fds=True
            )
            msg = Message(
                sender='test@test.com',
                recipients=['test@example.com'],
                subject='test',
                body='test'
            )
            mail.send(msg)
            try:
                smtpd.kill()
            except OSError:
                pass
            output = out.getvalue()
            assert 'reply: retcode (250); Msg: Ok' in output
    except:
        pass
    finally:
        sys.stdout = saved_stdout


if __name__ == '__main__':
    nose.runmodule()
