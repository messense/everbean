# -*- coding: utf-8 -*-
from __future__ import absolute_import, with_statement, unicode_literals
import os

import nose

from everbean.app import create_app
from everbean.ext.evernote import get_available_templates, get_template_name


def test_get_available_templates():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, 'config.py')

    app = create_app(config_file)
    with app.app_context():
        templates = get_available_templates()
        assert ('default', 'Default') in templates


def test_get_template_name():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, 'config.py')

    app = create_app(config_file)
    with app.app_context():
        template = get_template_name()
        assert template == 'default'
        template = get_template_name('doesnotexists')
        assert template == 'default'


if __name__ == '__main__':
    nose.runmodule()
