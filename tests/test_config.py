# coding=utf-8
import os
import nose
from everbean.app import create_app

base_dir = os.path.abspath(os.path.dirname(__file__))


def test_load_config_from_file():
    config_file = os.path.join(base_dir, 'config.py')
    app = create_app(config_file)
    with app.app_context():
        assert app.config['DOUBAN_API_KEY'] == 'test'
        assert app.config['EVERNOTE_CONSUMER_KEY'] == 'test'


def test_load_config_from_cwd():
    cwd = os.getcwd()
    os.chdir(base_dir)
    app = create_app()
    with app.app_context():
        assert app.config['DOUBAN_API_KEY'] == 'test'
        assert app.config['EVERNOTE_CONSUMER_KEY'] == 'test'
    os.chdir(cwd)


def test_load_config_from_dict():
    config = {
        'DOUBAN_API_KEY': 'test',
        'DOUBAN_API_SECRET': 'test',
        'DOUBAN_REDIRECT_URI': 'test',
        'EVERNOTE_CONSUMER_KEY': 'test',
        'EVERNOTE_CONSUMER_SECRET': 'test',
        'EVERNOTE_REDIRECT_URI': 'test',
        'SECRET_KEY': 'everbean-dev',
        'SQLALCHEMY_DATABASE_URI': 'mysql://root:root@localhost/everbean',
    }
    app = create_app(config)
    with app.app_context():
        assert app.config['DOUBAN_API_KEY'] == 'test'
        assert app.config['EVERNOTE_CONSUMER_KEY'] == 'test'


if __name__ == '__main__':
    nose.runmodule()
