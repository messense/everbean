# coding=utf-8
from __future__ import unicode_literals
import os
from fabric.api import *

base_path = os.path.dirname(__file__)
project_root = "~/projects/everbean"
pip_path = os.path.join(project_root, "bin/pip")
python_path = os.path.join(project_root, "bin/python")


env.user = "messense"
env.hosts = ["messense.me"]


def update_from_git():
    with cd(project_root):
        run("git pull --rebase")


def update_pip_requirements():
    with cd(project_root):
        run("%s install -U -r dev-requirements.txt" % pip_path)


def migrate_databases():
    with cd(project_root):
        run("%s manage.py syncdb" % python_path)
        run("%s manage.py db upgrade" % python_path)


def reload_nginx():
    sudo("/etc/init.d/nginx reload")


def restart_application():
    sudo("supervisorctl restart everbean")


def restart_worker():
    sudo("supervisorctl restart everbean_celery")


def reload_application():
    run("kill -HUP `cat /tmp/everbean.pid`")


def clear_cache():
    with cd(project_root):
        run("%s setup.py clean" % python_path)
        run("%s manage.py clear_cache" % python_path)
        run("%s manage.py assets clean" % python_path)
        run("%s manage.py assets build" % python_path)
        run("find . -name '*.pyc' -print0 | xargs -0 rm -rf")


def update():
    update_from_git()
    migrate_databases()
    clear_cache()
    reload_application()
    restart_worker()


def fullyupdate():
    update_from_git()
    update_pip_requirements()
    migrate_databases()
    clear_cache()
    reload_nginx()
    restart_application()
    restart_worker()


def minorupdate():
    update_from_git()
    clear_cache()
    reload_application()
    restart_worker()
