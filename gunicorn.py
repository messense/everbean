# coding=utf-8
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1

worker_class = 'gevent'
bind = "127.0.0.1:5000"

pidfile = "/tmp/everbean.pid"
