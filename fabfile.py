import os
from fabric.api import *

base_path = os.path.dirname(__file__)
project_root = "~/project/everbean"
pip_path = os.path.join(project_root, "bin/pip")
python_path = os.path.join(project_root, "bin/python")


env.user = "messense"
env.hosts = ["messense.me"]


def update_from_git():
    with cd(project_root):
        run("git pull --rebase")


def update_pip_requirements():
    with cd(project_root):
        run("%s install -U -r requirements.txt" % pip_path)
        run("%s install -U -r optional-requirements.txt" % pip_path)


def migrate_databases():
    with cd(project_root):
        run("%s manage.py db upgrade" % python_path)
        run("%s manage.py syncdb" % python_path)


def reload_nginx():
    _current_user = env.user
    env.user = 'root'
    run("/etc/init.d/nginx reload")
    env.user = _current_user


def restart_application():
    _current_user = env.user
    env.user = 'root'
    run("supervisorctl pid everbean | xargs kill -HUP")
    env.user = _current_user


def reload_application():
    run("kill -HUP `cat /tmp/everbean.pid`")


def update():
    update_from_git()
    migrate_databases()
    reload_application()


def fullyupdate():
    update_from_git()
    update_pip_requirements()
    migrate_databases()
    reload_nginx()
    reload_application()
